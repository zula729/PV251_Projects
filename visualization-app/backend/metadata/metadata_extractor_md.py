import re
import logging

from keybert import KeyBERT
from transformers import pipeline
from sklearn.feature_extraction.text import CountVectorizer

from utils import JsonYamlManager
from utils.paths import TAGS_YAML

logger = logging.getLogger(__name__)


class MarkdownExtractor:
    def __init__(self, model_name: str = 'distilbert-base-nli-mean-tokens'):
        self.model = KeyBERT(model_name)
        self.vectorizer = CountVectorizer(
            token_pattern=r"(?u)\b[^\W\d_]{2,}\b"
        )
        self.ner = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")

    def _get_field(self, content: dict, key: str, default: str = "") -> str:
        value = content.get(key)
        if value is None:
            logger.warning(f"No '{key}' in content")
            return default
        return value

    def _predict_keywords(self, text: str, top_n: int = 5) -> list[str]:
        results = self.model.extract_keywords(
            text,
            top_n=top_n,
            vectorizer=self.vectorizer,
        )
        return [kw for kw, _ in results]
    
    def _match_known_keywords(self, content: str) -> list[str]:
        try:
            tags = JsonYamlManager.load_yaml(TAGS_YAML)
            found_keywords = set()
            for _, examples in tags.items():
                for example in examples:
                    if example.lower() in content:
                        found_keywords.add(example)
            return list(found_keywords)
        except Exception as e:
            logger.error(f"Error processing known keywords: {e}")
            return []
    
    def extract_keywords(self, content: dict) -> dict[str, list[str]] | None:
        try:
            text = (
                self._get_field(content, "Motivation") +
                self._get_field(content, "Project Description (short project description 150-200 words)") +
                self._get_field(content, "Explanation of the design choices")
            )
            keywords: list[str] = (self._predict_keywords(text))
            extracted_keywords: list[str] = self._match_known_keywords(text)
            merged = set(keywords + extracted_keywords)
            return {"keywords": list(merged)} 
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return None
    
    def extract_tags(self, content: dict):
        text = (
                self._get_field(content, "Motivation") +
                self._get_field(content, "Project Description (short project description 150-200 words)") +
                self._get_field(content, "Explanation of the design choices")
            )
        tags = JsonYamlManager.load_yaml(TAGS_YAML)
        found_tags = set()
        for tag, examples in tags.items():
            for example in examples:
                if example.lower() in text:
                    found_tags.add(tag)
        return list(found_tags)

    def extract_metadata(self, content: dict[str, str | None]):
        authors_raw = self._get_field(content, "Authors")
        tech_raw = self._get_field(content, "Used technologies")
        
        return {
            "name": self._get_field(content, "name"),
            "author": [line.lstrip("- ").strip() for line in authors_raw.split("\n") if line.strip()],
            "technology": [re.sub(r"^\d+\.\s+", "", line) for line in tech_raw.split("\n") if line.strip()],
            "text": self._get_field(content, "Project Description (short project description 150-200 words)"),
            "link": self._get_field(content, "Link on project"),
            "tags": self.extract_tags(content),

        }


def main():
    # md_pr = MarkdownExtractor()
    # path = Path(r"C:\Users\azhar\Desktop\example\511868-Danisova_Terezie-AMR_project_Danisova_Chupac_Postulka\AMR_project_Danisova_Chupac_Postulka\report.md")
    # content = md_pr.parse_sections(path)
    # print(md_pr.extract_metadata(content))
    # print(20 * "-")
    # print(md_pr.extract_keywords(content))
    pass

main()