from keybert import KeyBERT # type: ignore
from pathlib import Path
import fitz  # type: ignore
import docx
import json
import firebase_admin # type: ignore
from firebase_admin import credentials, db  # type: ignore
from sklearn.feature_extraction.text import CountVectorizer, ENGLISH_STOP_WORDS # type: ignore
import re
from wordfreq import zipf_frequency # type: ignore
import yaml
from transformers import pipeline

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class DocumentProcessor:
    def read_text(self, file_path: Path) -> str:
        if file_path.suffix.lower() == '.pdf':
            return self._read_pdf(file_path)
        elif file_path.suffix.lower() == '.docx':
            return self._read_docx(file_path)
        return ""

    def _read_pdf(self, path: Path):
        doc = fitz.open(path)
        return "".join(page.get_text() for page in doc)
    
    def _read_docx(self, path: Path):
        doc = docx.Document(path)
        return "".join(para.text for para in doc.paragraphs)


class KeywordExtractor:
    def __init__(self, model_name: str = 'distilbert-base-nli-mean-tokens'):
        self.model = KeyBERT(model_name)
        self.vectorizer = CountVectorizer(
            token_pattern=r"(?u)\b[^\W\d_]{2,}\b"  # words only, no numbers
        )

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
            if part[0].isdigit():
                return part[:6]
        return None

    def extract_from_file(
        self, file_path: Path, doc_processor: DocumentProcessor) -> tuple[list[str], str] | tuple[None, None]:
        if self.is_macos_artifact(file_path):
            return None, None
        try:
            folder_id = self.folder_id_from_path(file_path)
            text = doc_processor.read(file_path)
            keywords = self.extract(text)
            return keywords, folder_id
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
            return [], ''
    
    def extract_authors_from_folder_name(folder_name: str):
        # Паттерн: цифры, потом дефис, потом текст до следующего дефиса или конца
        # Мы ищем то, что идет СРАЗУ после первых цифр и дефиса
        match = re.search(r'^\d+-(.*?)(?:-|$)', folder_name)
        
        if match:
            raw_names = match.group(1) # Получаем "Pekar_Matej-pekar_boril" или "Burlutskyi_Ivan-Burlutskyi-Beranger..."
            
            # Заменяем нижнее подчеркивание на пробел и чистим дефисы
            # Чтобы из "Pekar_Matej" получить "Pekar Matej"
            clean_names = raw_names.replace('_', ' ').replace('-', ', ')
            return clean_names
        return "Unknown Author"


class FirebaseClient:
    DB_URL = "https://visualization-88a6b-default-rtdb.europe-west1.firebasedatabase.app/"
    REF_PATH = "Keywords from projects"

    def __init__(self, cred_path: str = "credentials.json"):
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {"databaseURL": self.DB_URL})
        self.ref = db.reference(self.REF_PATH)

    def upload(self, files: list[Path], extractor: KeywordExtractor, doc_processor: DocumentProcessor):
        for file_path in FILES:
            keywords, folder_id = extractor.extract_keywords(file_path, doc_processor)
            if keywords is None:
                print("NONE VALUE TO DATA BASE")
                continue
            # db_key = f"{folder_id}"
            # self.ref.child(db_key).set({
            #     "keywords": keywords,
            #     "semester": self.get_semester(file_path),
            # })
            self.ref.child(folder_id).set({
                "keywords": keywords,
                "semester": self._get_semester(file_path),
            })

    @staticmethod
    def _get_semester(path: Path) -> str | None:
        for part in path.parts:
            if part.lower().startswith("podzim"):
                return part
        return None
    # def check_counts(self, json_path: str) -> None:
    #     with open(json_path, 'r', encoding='utf-8') as f:
    #         json_count = len(json.load(f))
    #     db_data = self.ref.get()
    #     db_count = len(db_data) if db_data else 0
    #     print(f"JSON keys: {json_count} | Firebase keys: {db_count} | Diff: {json_count - db_count}")


class KeywordFilter:
    def filter(self, keywords: list[str]) -> list[str]:
        return [kw for kw in keywords if self._is_valid(kw)]

    def _is_valid(self, kw: str) -> bool:
        if re.search(r"\d", kw):          # reject anything with digits
            return False
        if " " in kw:                      # multi-word phrases always pass
            return True
        return self._is_real_word(kw)

    def _is_real_word(word: str) -> bool:
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
    def extract_authors(folder_name: str) -> str:
        """Parse 'ID-Surname_Name-surname_name-...' folder names into author strings."""
        match = re.search(r'^\d+-(.*?)(?:-|$)', folder_name)
        if match:
            return match.group(1).replace('_', ' ').replace('-', ', ')
        return "Unknown Author"

    @staticmethod
    def save_keywords_json(
        files: list[Path],
        extractor: KeywordExtractor,
        doc_processor: DocumentProcessor,
        output_path: str = "keywords.json",
    ) -> None:
        keywords_dict: dict[str, list[str]] = {}
        for file_path in files:
            keywords, folder_id = extractor.extract_from_file(file_path, doc_processor)
            if folder_id is not None:
                keywords_dict[folder_id] = keywords or []
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


def main() -> None:
    pipeline = Pipeline(
        root_dir=Path(r'C:\Users\azhar\Desktop\visualization'),
        cred_path="credentials.json",
    )
    # -- quick author-extraction smoke test --
    folders = [
        "525077-Pekar_Matej-pekar_boril",
        "525221-Lodnanova_Michaela-project",
        "532094-Burlutskyi_Ivan-Burlutskyi-Beranger-SelimcanBicer",
    ]
    for f in folders:
        print(f"Folder: {f} -> Author: {ProjectUtils.extract_authors(f)}")

    # Uncomment the steps you want to run:
    # pipeline.run_export_json()
    # pipeline.run_upload()
    # result = pipeline.run_categorize("keywords.json", "tags.yaml")
    # print(result)

if __name__ == "__main__":
    main()
