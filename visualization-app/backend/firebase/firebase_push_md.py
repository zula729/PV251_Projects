import firebase_admin
from firebase_admin import credentials, db, storage
from pathlib import Path
from utils import PathParser
import re

from pathlib import Path

import logging

logger = logging.getLogger(__name__)


class FirebasePushMD:
    DB_URL = "https://visualization-88a6b-default-rtdb.europe-west1.firebasedatabase.app/"
    REF_PATH = "Keywords from projects"
    BUCKET_NAME = "visualization-88a6b.firebasestorage.app"
    DEFAULT_CRED = Path(__file__).parent.parent / "credentials.json"

    def __init__(self, cred_path: Path = DEFAULT_CRED):
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {"databaseURL": self.DB_URL, "storageBucket": self.BUCKET_NAME})
        self.ref = db.reference(self.REF_PATH)
    
    def parse_sections(self, file_path: Path) -> dict[str, str | None]:
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            project_name = re.search(r'^#\s+(.+)', content, re.MULTILINE)
            sections = re.split(r'^##\s+', content, flags=re.MULTILINE)
            result = {"name": project_name.group(1).strip() if project_name else None}
            for section in sections[1:]:
                lines = section.strip().split('\n')
                heading = lines[0].strip()
                body = '\n'.join(lines[1:]).strip()
                result[heading] = body if body else None
            return result
        except Exception as e:
            logging.error(f"Error reading file {file_path} : {e}")
            return None
    
    def _merge_and_push(self, folder_id: str, data: dict[str, list[str]]) -> None:
        current = self.ref.child(folder_id).get() or {}
        merged_data = {}
        for key, values in data.items():
            existing = current.get(key, [])
            if isinstance(existing, list) and isinstance(values, list):
                merged_data[key] = list(set(existing + values))
            else:
                merged_data[key] = values
        self.ref.child(folder_id).update(merged_data)
    
    def push_metadata(self, files: list[Path]):
        from metadata import MarkdownExtractor
        from utils import PathParser
        extractor = MarkdownExtractor()
        util = PathParser()
        for file_path in files:
            content = self.parse_sections(file_path)
            data_to_send = extractor.extract_metadata(content)
            data_to_send.update({"semester": util.extract_semester(file_path)})

            folder_id = PathParser.extract_folder_id(file_path)
            if not folder_id:
                logging.error(f"Error: {file_path}")
                continue
            self._merge_and_push(folder_id, data_to_send)

    def push_keywords(self, files: list[Path]):
        from metadata import MarkdownExtractor
        extractor = MarkdownExtractor()
        for file_path in files:
            content = self.parse_sections(file_path)
            keywords = extractor.extract_keywords(content)
            if keywords is None:
                logging.warning(f"NONE VALUE TO DATA BASE: {file_path}")
                continue
            folder_id = PathParser.extract_folder_id(file_path)
            if not folder_id:
                logging.warning(f"Error: {file_path}")
                continue
            self._merge_and_push(folder_id, keywords)
    
    def push_images(self, files: list[Path]):
        bucket = storage.bucket()
        urls_by_folder: dict[str, list[str]] = {}

        for file_path in files:
            try: 
                folder_id = PathParser.extract_folder_id(file_path)
                blob = bucket.blob(f"{folder_id}/{file_path.name}")
                blob.upload_from_filename(str(file_path))
                blob.make_public()

                urls_by_folder.setdefault(folder_id, []).append(blob.public_url)
            except Exception as e:
                logging.error(f"Error uploading {file_path.name}: {e}")

        for folder_id, urls in urls_by_folder.items():
            try:
                self._merge_and_push(folder_id, {"images": urls})
            except Exception as e:
                logging.error(f"Error updating database for {folder_id}: {e}")
