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

TECH_TERMS = {
    "python", "javascript", "typescript", "java", "r", "sql",
    "d3", "d3.js", "react", "vue", "angular", "svelte",
    "pandas", "numpy", "matplotlib", "plotly", "tableau",
    "firebase", "postgresql", "mongodb", "mysql",
    "docker", "kubernetes", "git", "github",
    "sklearn", "tensorflow", "pytorch", "keras",
    "figma", "powerbi", "excel", "powerpoint",
    "flask", "django", "fastapi", "node", "express",
}

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
            token_pattern=r"(?u)\b[^\W\d_]{2,}\b"
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
            if p.startswith("__macosx") or p.startswith("._") or p == ".ds_store" or p == "__MACOSX":
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
    
    ## does not working, woking bad with difficult names
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

    @staticmethod
    def extract_technology(path: Path) -> str:
        # extract python, D3, and others techlology
        pass

    def extract_keywords_from_file(self, file_path: Path, doc_processor: DocumentProcessor
        ) -> tuple[list[str], str, str] | tuple[None, None, None]:
        if self.is_macos_artifact(file_path):
            return None, None, None
        try:
            text = doc_processor.read_text(file_path)
            keywords = self.extract(text)
            return keywords
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
            return [], ''

    def extract_metadata(self, file_path: Path):
        if self.is_macos_artifact(file_path):
            return None, None, None
        try:
            folder_id = self.folder_id_from_path(file_path)
            author = self.extract_authors_from_name(file_path)
            technology = self.extract_technology(file_path)
            return folder_id, author, technology
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
            return [], ''

class KeywordFilter:
    def filter(self, keywords: set[str]) -> list[str]:
        return [kw for kw in keywords if self._is_valid(kw)]

    def _is_valid(self, kw: str) -> bool:
        if re.search(r"\d", kw):          # reject anything with digits
            return False
        if " " in kw:                      # multi-word phrases always pass
            return True
        return self._is_real_word(kw)

    def _is_real_word(self, word:    str) -> bool:
        return zipf_frequency(word, "en") > 2.5 or zipf_frequency(word, "cs") > 2.5 

class FirebaseClient:
    DB_URL = "https://visualization-88a6b-default-rtdb.europe-west1.firebasedatabase.app/"
    REF_PATH = "Keywords from projects"

    def __init__(self, cred_path: str = "credentials.json"):
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {"databaseURL": self.DB_URL})
        self.ref = db.reference(self.REF_PATH)

    def upload_metadata(self, files: list[Path], extractor: KeywordExtractor):
        for file_path in files:
            folder_id, author, technology = extractor.extract_metadata(file_path)
            self.ref.child(f"{folder_id}").update({
                "semester": self._get_semester(file_path),
                "author": author, 
                "technology": technology, 
            })

    def upload_keywords(self, files: list[Path], extractor: KeywordExtractor, doc_processor: DocumentProcessor, keyword_filer: KeywordFilter):
        for file_path in files:
            keywords = extractor.extract_keywords_from_file(file_path, doc_processor)
            folder_id = extractor.folder_id_from_path(file_path)
            if keywords is None:
                print("NONE VALUE TO DATA BASE")
                print(file_path)
                continue
            if keywords == "":
                print("WRONG PDF OR DOCX FILE")
                print(file_path)
                continue
            keywords = keyword_filer.filter(keywords)
            self.ref.child(f"{folder_id}").update({
                "keywords": keywords,
            })

    @staticmethod
    def _get_semester(path: Path) -> str | None:
        for part in path.parts:
            if part.lower().startswith("podzim"):
                return part
        return None

    def fetch_all(self) -> dict:
        return self.ref.get() or {}

class KeywordClassifier:
    def __init__(self, model_name: str = "cross-encoder/nli-deberta-v3-large", threshold: float = 0.5):
        self.classifier = pipeline("zero-shot-classification", model=model_name)
        self.threshold = threshold
        self._cache: dict[str, str] = {}  # simple dict cache

    def categorize(
        self, keywords: set[str], categories: dict[str, list[str]]
    ) -> dict[str, list[str]]:
        """Assign each keyword to the best-matching category."""
        categorized: dict[str, list[str]] = {cat: [] for cat in categories}
        labels = self._build_labels(categories)

        for kw in keywords:
            cat = self._classify_single(kw, labels)
            categorized.setdefault(cat, []).append(kw)
        return categorized

    def _classify_single(self, word: str, candidate_labels: list[str]) -> str:
        if word in self._cache:
            return self._cache[word]
        
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
        keyword_filter: KeywordFilter,
        output_path: str = "keywords.json",
    ) -> None:
        keywords_dict: dict[str, list[str]] = {}
        for file_path in files:
            keywords = extractor.extract_keywords_from_file(file_path, doc_processor)
            folder_id, author, technology = extractor.extract_metadata(file_path)
            if keywords is None:
                print("NONE VALUE TO DATA BASE")
                print(file_path)
                continue
            if keywords == "":
                print("WRONG PDF OR DOCX FILE")
                print(file_path)
                continue 
            keywords = keyword_filter.filter(keywords)
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
    
    @staticmethod
    def repair_pdf(input_path: Path, output_path: Path) -> None:
        ocrmypdf.ocr(
            input_path,
            output_path,
            force_ocr=True,       # re-OCR even if text layer exists
            language="eng+ces",   # English + Czech
            deskew=True,
        )

    def repair_all_pdfs(self, root_dir: Path) -> None:
        for pdf in root_dir.rglob("*.pdf"):
            tmp = pdf.with_suffix(".tmp.pdf")
            try:
                self.repair_pdf(pdf, tmp)
                tmp.replace(pdf)
                print(f"Repaired: {pdf.name}")
            except Exception as e:
                tmp.unlink(missing_ok=True)
                print(f"Failed: {pdf.name} — {e}")
    
    @staticmethod
    def save_categories_yaml(data: dict, output_path: str = "categorized_keywords.yaml") -> None:
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)


class Pipeline:
    def __init__(self, root_dir: Path, cred_path: str = "credentials.json"):
        self.root_dir = root_dir
        self.doc_processor = DocumentProcessor()
        self.keyword_filter = KeywordFilter()
        self.firebase = FirebaseClient(cred_path)
        self.utils = ProjectUtils()
        self._extractor = None    # lazy
        self._classifier = None   # lazy
    
    @property
    def extractor(self) -> KeywordExtractor:
        if self._extractor is None:
            self._extractor = KeywordExtractor()
        return self._extractor

    @property
    def classifier(self) -> KeywordClassifier:
        if self._classifier is None:
            self._classifier = KeywordClassifier()
        return self._classifier
    
    @property
    def files(self) -> list[Path]:
        all_files = list(self.root_dir.rglob('*.pdf')) + list(self.root_dir.rglob('*.docx'))
        result = []
        for f in all_files:
            if "report" in f.name.lower():
                result.append(f)
        return result

    def run_upload(self) -> None:
        self.firebase.upload_keywords(self.files, self.extractor, self.doc_processor, self.keyword_filter)
        self.firebase.upload_metadata(self.files, self.extractor)

    def run_export_json(self, output_path: str = "keywords.json") -> None:
        self.utils.save_keywords_json(self.files, self.extractor, self.doc_processor, self.keyword_filter, output_path)

    def run_categorize(self, yaml_path: str) -> None:
        db_data = self.firebase.fetch_all()

        kw1 = set()
        for _, data in db_data.items():
            kw_list = data.get('keywords')
            if isinstance(kw_list, list):
                kw1.update(kw_list)

        tags = self.utils.load_categories(yaml_path)

        kw2: set[str] = set()
        for _, data in tags.items():
            if isinstance(data, list):
                kw2.update(data)

        keywords_not_in_tags: set[str] = kw1 - kw2

        final_result: dict[str, list[str]] = {
            cat: list(examples) if examples else []
            for cat, examples in tags.items()
        }
        final_result["UNDEFINED"] = []

        # result without existing examples — only newly classified words
        result_clean: dict[str, list[str]] = {cat: [] for cat in tags}
        result_clean["UNDEFINED"] = []

        # hypotheses se sestaví JEDNOU před hlavním looopem
        hypotheses = [
            f"This text is about {cat}, such as {', '.join(examples if isinstance(examples, list) else [])}."
            for cat, examples in tags.items()
        ]
        cat_names = list(tags.keys())

        for kw in keywords_not_in_tags:
            result = self.classifier.classifier(
                kw,
                candidate_labels=hypotheses,
                multi_label=False,
                hypothesis_template="{}"
            )
            scores = {
                cat_names[hypotheses.index(label)]: score
                for label, score in zip(result['labels'], result['scores'])
            }
            best_cat = max(scores, key=scores.get)
            best_score = scores[best_cat]
            chosen = best_cat if best_score >= 0.6 else "UNDEFINED"
            final_result[chosen].append(kw)
            result_clean[chosen].append(kw)
            print(f"{kw} → {chosen} (score: {best_score:.2f})")

        self.utils.save_categories_yaml(result_clean)

def main() -> None:
    pipeline = Pipeline(
        root_dir=Path(r'C:\Users\azhar\Desktop\visualization'),
        cred_path="credentials.json",
    )

if __name__ == "__main__":
    main()
