import docx
import json
import firebase_admin
import sys
import io
import re
import pdfplumber
import yaml
import ocrmypdf
from wordfreq import zipf_frequency
from firebase_admin import credentials, db
from sklearn.feature_extraction.text import CountVectorizer
from transformers import pipeline
from keybert import KeyBERT
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class DocumentProcessor:
    def read_text(self, file_path: Path) -> str:
        if file_path.suffix.lower() == '.pdf':
            return self._read_pdf(file_path)
        if file_path.suffix.lower() == '.docx':
            return self._read_docx(file_path)
        return ""

    def _read_pdf(self, path: Path) -> str:
        with pdfplumber.open(path) as pdf:
            return "".join(page.extract_text() or "" for page in pdf.pages)

    def _read_docx(self, path: Path):
        doc = docx.Document(path)
        return "".join(para.text for para in doc.paragraphs)


class KeywordExtractor:
    def __init__(self, model_name: str = 'distilbert-base-nli-mean-tokens'):
        self.model = KeyBERT(model_name)
        self.vectorizer = CountVectorizer(
            token_pattern=r"(?u)\b[^\W\d_]{2,}\b"  # words only, no numbers
        )
        self.ner = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")


    def extract(self, text: str, top_n: int = 5) -> list[str]:
        results = self.model.extract_keywords(
            text,
            top_n=top_n,
            vectorizer=self.vectorizer,
        )
        return [kw for kw, _score in results]

    @staticmethod
    def is_macos_artifact(path: Path) -> bool:
        for part in path.parts:
            p = part.lower()
            if p.startswith("__macosx") or p.startswith("._") or p == ".ds_store":
                return True
        return False

    @staticmethod
    def folder_id_from_path(path: Path) -> str | None:
        for part in path.parts:
            if part[0].isdecimal():
                return part[:6]
        return None
    
    @staticmethod
    def _clean_name(name: str) -> str:
        name = re.sub(r'##', '', name)
        name = re.sub(r'\s+', ' ', name)
        name = name.strip()
        return name
    
    def extract_authors_from_file(self, text: str) -> str:
        entities = self.ner(text)
        names = [
            self._clean_name(e["word"])
            for e in entities
            if e["entity_group"] == "PER"
        ]
        names = [n for n in names if len(n) > 1]  # drop single chars
        return ', '.join(dict.fromkeys(names)) if names else "Unknown Author"

    @staticmethod
    def extract_authors_from_name(path: Path) -> str:
        """Parse 'ID-Surname_Name-surname_name-...' folder names into author strings."""
        for part in path.parts:
            if part[0].isdecimal():
                match = re.search(r'^\d+-(.*?)(?:-|$)', part)
                if match:
                    return match.group(1).replace('_', ' ').replace('-', ', ')
        return "Unknown Author"

    def extract_from_file(
            self,
            file_path: Path,
            doc_processor: DocumentProcessor
        ) -> tuple[list[str], str, str] | tuple[None, None, None]:
        if self.is_macos_artifact(file_path):
            return None, None, None
        try:
            folder_id = self.folder_id_from_path(file_path)
            text = doc_processor.read_text(file_path)
            keywords = self.extract(text)
            ## Tady musim pridat rozlisovani podle skupinovych projektu a single, zatim funguje jen single
            author = self.extract_authors_from_name(file_path)
            return keywords, folder_id, author
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
            return [], ''


class FirebaseClient:
    DB_URL = "https://visualization-88a6b-default-rtdb.europe-west1.firebasedatabase.app/"
    REF_PATH = "Keywords from projects"

    def __init__(self, cred_path: str = "credentials.json"):
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {"databaseURL": self.DB_URL})
        self.ref = db.reference(self.REF_PATH)

    def upload(self, files: list[Path], extractor: KeywordExtractor, doc_processor: DocumentProcessor):
        for file_path in files:
            keywords, folder_id, author = extractor.extract_from_file(file_path, doc_processor)
            if keywords is None or folder_id is None:
                print("NONE VALUE TO DATA BASE")
                print(file_path)
                continue
            self.ref.child(f"{folder_id}").set({
                "keywords": keywords,
                "semester": self._get_semester(file_path),
                "author": author
            })

    @staticmethod
    def _get_semester(path: Path) -> str | None:
        for part in path.parts:
            if part.lower().startswith("podzim"):
                return part
        return None


class KeywordFilter:
    def filter(self, keywords: list[str]) -> list[str]:
        return [kw for kw in keywords if self._is_valid(kw)]

    def _is_valid(self, kw: str) -> bool:
        if re.search(r"\d", kw):          # reject anything with digits
            return False
        if " " in kw:                      # multi-word phrases always pass
            return True
        return self._is_real_word(kw)

    def _is_real_word(self, word: str) -> bool:
        return zipf_frequency(word, "en") > 2.5 or zipf_frequency(word, "cs") > 2.5 


class KeywordClassifier:
    def __init__(self, model_name: str = "facebook/bart-large-mnli", threshold: float = 0.3):
        self.classifier = pipeline("zero-shot-classification", model=model_name)
        self.threshold = threshold

    def categorize(
        self, keywords: list[str], categories: dict[str, list[str]]
    ) -> dict[str, list[str]]:
        """Assign each keyword to the best-matching category."""
        categorized: dict[str, list[str]] = {cat: [] for cat in categories}
        labels = self._build_labels(categories)

        for kw in keywords:
            cat = self._classify_single(kw, labels)
            categorized.setdefault(cat, []).append(kw)
        return categorized

    def _classify_single(self, word: str, candidate_labels: list[str]) -> str:
        result = self.classifier(word, candidate_labels=candidate_labels, multi_label=False)
        best_label: str = result["labels"][0]
        best_score: float = result["scores"][0]
        if best_score >= self.threshold:
            return best_label.split(":")[0]
        return "UNDEFINED"

    @staticmethod
    def _build_labels(categories: dict[str, list[str]]) -> list[str]:
        labels = []
        for cat, words in categories.items():
            if words:
                label = f"{cat}: {', '.join(str(w) for w in words)}"
            else:
                label = cat
            labels.append(label)
        return labels


class ProjectUtils:
    @staticmethod
    def save_keywords_json(
        files: list[Path],
        extractor: KeywordExtractor,
        doc_processor: DocumentProcessor,
        output_path: str = "keywords.json",
    ) -> None:
        keywords_dict: dict[str, list[str]] = {}
        for file_path in files:
            keywords, folder_id, author= extractor.extract_from_file(file_path, doc_processor)
            if folder_id is not None:
                keywords_dict[folder_id] = keywords, author or []
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(keywords_dict, f, ensure_ascii=False, indent=2)

    @staticmethod
    def load_json(file_path: str) -> dict:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def load_categories(yaml_path: str) -> dict[str, list[str]]:
        with open(yaml_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)


class Pipeline:
    def __init__(self, root_dir: Path, cred_path: str = "credentials.json"):
        self.root_dir = root_dir
        self.doc_processor = DocumentProcessor()
        self.extractor = KeywordExtractor()
        self.keyword_filter = KeywordFilter()
        self.classifier = KeywordClassifier()
        self.firebase = FirebaseClient(cred_path)
        self.utils = ProjectUtils()

    @property
    def files(self) -> list[Path]:
        return list(self.root_dir.rglob('*.pdf')) + list(self.root_dir.rglob('*.docx'))

    def run_upload(self) -> None:
        self.firebase.upload(self.files, self.extractor, self.doc_processor)

    def run_export_json(self, output_path: str = "keywords.json") -> None:
        self.utils.save_keywords_json(self.files, self.extractor, self.doc_processor, output_path)

    def run_categorize(self, json_path: str, yaml_path: str) -> dict[str, list[str]]:
        categories = self.utils.load_categories(yaml_path)
        all_keywords: list[str] = [
            kw
            for kws in self.utils.load_json(json_path).values()
            for kw in kws
        ]
        return self.classifier.categorize(all_keywords, categories)

def repair_pdf(input_path: Path, output_path: Path) -> None:
        ocrmypdf.ocr(
            input_path,
            output_path,
            force_ocr=True,       # re-OCR even if text layer exists
            language="eng+ces",   # English + Czech
            deskew=True,
        )

def repair_all_pdfs(self, root_dir: Path) -> None:
    repaired_dir = root_dir / "repaired"
    repaired_dir.mkdir(exist_ok=True)
    for pdf in root_dir.rglob("*.pdf"):
        out = repaired_dir / pdf.name
        try:
            self.repair_pdf(pdf, out)
            print(f"Repaired: {pdf.name}")
        except Exception as e:
            print(f"Failed: {pdf.name} — {e}")


def main() -> None:
    pipeline = Pipeline(
        root_dir=Path(r'C:\Users\azhar\Desktop\visualization'),
        cred_path="credentials.json",
    )
    # pipeline.run_upload()
    pipeline.run_export_json()
    # files = pipeline.files
    # repair_pdf(r"C:\Users\azhar\Desktop\visualization\podzim2024\524688-Kraus_Jozef-FeelViz\Visualization_Short_Report.pdf", r"C:\Users\azhar\Desktop\repair\report_fixed.pdf")
    # for f in folders:
    #     print(f"Folder: {f} -> Author: {ProjectUtils.extract_authors(f)}")
    # file_path_name_text = r"C:\Users\azhar\Desktop\visualization\podzim2025\484353-Kutalek_Jiri-ProjectFiles_Group4_Demovic_Kutalek_Polak\pv251_footballviz-main\report.pdf"
    # a = pipeline.utils.extract_authors_from_file(Path(file_path_name_text), pipeline.doc_processor)
    # print(a)
    # Uncomment the steps you want to run:
    # pipeline.run_export_json()
    # pipeline.run_upload()
    # result = pipeline.run_categorize("keywords.json", "tags.yaml")
    # print(result)

if __name__ == "__main__":
    main()
