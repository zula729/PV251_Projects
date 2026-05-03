from firebase import FirebasePushPDF
from utils import JsonYamlManager

from transformers import pipeline


class KeywordClassifier:
    def __init__(self, score_threshold: float = 0.6):
        self.classifier = pipeline("zero-shot-classification")
        self.score_threshold = score_threshold

    def run_categorize(self, yaml_path: str, firebase: FirebasePushPDF) -> None:
        db_keywords = self._extract_firebase_keywords(firebase)
        tags = JsonYamlManager.load_yaml(yaml_path)
        tag_keywords = self._extract_tag_keywords(tags)
        undefined_keywords = db_keywords - tag_keywords
        result_clean = self._classify_keywords(undefined_keywords, tags)
        JsonYamlManager.save_yaml(result_clean)

    def _extract_firebase_keywords(self, firebase: FirebasePushPDF) -> set[str]:
        keywords = set()
        db_data = firebase.fetch_all()
        for _, data in db_data.items():
            kw_list = data.get('keywords')
            keywords.update(kw_list)
        return keywords

    def _extract_tag_keywords(self, tags: dict) -> set[str]:
        keywords = set()
        for _, data in tags.items():
            if isinstance(data, list):
                keywords.update(data)
        return keywords

    def _classify_keywords(self, keywords: set[str], tags: dict) -> dict:
        result = {cat: [] for cat in tags}
        result["UNDEFINED"] = []

        hypotheses = self._build_hypotheses(tags)
        cat_names = list(tags.keys())

        for keyword in keywords:
            category = self._classify_single_keyword(
                keyword, hypotheses, cat_names
            )
            result[category].append(keyword)
            print(f"{keyword} → {category}")

        return result

    def _build_hypotheses(self, tags: dict) -> list[str]:
        return [
            f"This text is about {cat}, such as {', '.join(ex if isinstance(ex, list) else [])}."
            for cat, ex in tags.items()
        ]

    def _classify_single_keyword(
        self,
        keyword: str,
        hypotheses: list[str],
        categories: list[str]
    ) -> str:
        result = self.classifier(
            keyword,
            candidate_labels=hypotheses,
            multi_label=False,
            hypothesis_template="{}"
        )

        scores = {
            categories[hypotheses.index(label)]: score
            for label, score in zip(result['labels'], result['scores'])
        }

        best_category = max(scores, key=scores.get)
        best_score = scores[best_category]

        return best_category if best_score >= self.score_threshold else "UNDEFINED"
