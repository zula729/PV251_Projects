import firebase_admin
from firebase_admin import credentials, db, storage
from pathlib import Path

from utils import PathParser


class FirebasePushPDF:
    DB_URL = "https://visualization-88a6b-default-rtdb.europe-west1.firebasedatabase.app/"
    REF_PATH = "Keywords from projects"
    BUCKET_NAME = "visualization-88a6b.firebasestorage.app"
    DEFAULT_CRED = Path(__file__).parent.parent / "credentials.json"

    def __init__(self, cred_path: Path = DEFAULT_CRED):
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {"databaseURL": self.DB_URL, "storageBucket": self.BUCKET_NAME})
        self.ref = db.reference(self.REF_PATH)

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

    def push_metadata(self, files: list[Path], extractor, doc_processor):
        for file_path in files:
            if PathParser.is_macos_artifact(file_path):
                continue
            data_to_send = extractor.extract_metadata(file_path, doc_processor)
            folder_id = PathParser.extract_folder_id(file_path)
            if not folder_id:
                print(f"Error: {file_path}")
                continue
            self._merge_and_push(folder_id, data_to_send)

    def push_keywords(self, files: list[Path], extractor, doc_processor):
        for file_path in files:
            if PathParser.is_macos_artifact(file_path):
                continue
            text = doc_processor.read_text(file_path).lower()
            keywords = (extractor.extract_keywords(text))
            if keywords is None or keywords == "":
                print(f"NONE VALUE TO DATA BASE: {file_path}")
                continue
            
            folder_id = PathParser.extract_folder_id(file_path)
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
                print(f"Error uploading {file_path.name}: {e}")

        for folder_id, urls in urls_by_folder.items():
            try:
                self._merge_and_push(folder_id, {"images": urls})
            except Exception as e:
                print(f"Error updating database for {folder_id}: {e}")
