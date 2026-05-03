from pathlib import Path
import yaml

class JsonYamlManager:
    @staticmethod
    def save_yaml(data: dict, output_path: str = "categorized_keywords.yaml") -> None:
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

    @staticmethod
    def load_yaml(path: Path) -> dict[str, list[str]]:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
