import firebase_admin
from firebase_admin import credentials, db, storage
from pathlib import Path
from utils import JsonYamlManager
import logging

logger = logging.getLogger(__name__)


class FirebaseClient:
    DB_URL = "https://visualization-88a6b-default-rtdb.europe-west1.firebasedatabase.app/"
    REF_PATH = "Keywords from projects"
    BUCKET_NAME = "visualization-88a6b.firebasestorage.app"
    DEFAULT_CRED = Path(__file__).parent.parent / "credentials.json"

    def __init__(self, cred_path: Path = DEFAULT_CRED):
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {"databaseURL": self.DB_URL, "storageBucket": self.BUCKET_NAME})
        self.ref = db.reference(self.REF_PATH)

    def fetch_all(self) -> dict:
        return self.ref.get() or {}

    def delete_empty_records(self) -> None:
        data = self.fetch_all()
        for folder_id, entry in data.items():
            if not entry.get("keywords"):
                self.ref.child(folder_id).delete()
                logger.info(f"Deleted: {folder_id}")

    def filter_keywords_by_yaml(self, yaml_path: str, dry_run: bool = True) -> None:
        categories = JsonYamlManager.load_categories(yaml_path)
        allowed: set[str] = self._get_allowed_keywords(categories)

        db_data = self.fetch_all()
        total_removed = 0

        for folder_id, entry in db_data.items():
            removed = self._filter_entry_keywords(folder_id, entry, allowed, dry_run)
            total_removed += removed

        return total_removed

    def _get_allowed_keywords(self, categories: dict) -> set[str]:
        allowed = set()
        for examples in categories.values():
            allowed.update(self._ensure_list(examples))
        return allowed

    def _filter_entry_keywords(self, folder_id: str, entry: dict, allowed: set[str], dry_run: bool) -> int:
        kw_list = entry.get("keywords", [])
        to_remove = [kw for kw in kw_list if kw not in allowed]
        if not kw_list or not to_remove:
            logger.warning(f"")
 
        if not dry_run:
            cleaned = [kw for kw in kw_list if kw in allowed]
            self._merge_and_push(folder_id, {"keywords": cleaned})
 
        return len(to_remove)

    def find_missing_folders(self, root_dir: Path):
        local_ids = self._scan_local_folders(root_dir)
        db_ids = set(self.fetch_all().keys())

        missing = {fid: name for fid, name in local_ids.items() if fid not in db_ids}

        if missing:
            logger.warning(f"not in database ({len(missing)}):")
            for fid, name in sorted(missing.items()):
                logger.warning(f"{fid}->{name}")
        return missing

    def _scan_local_folders(self, root_dir: Path) -> dict[str, str]:
        local_ids = {}
        for semester in root_dir.iterdir():
            for folder in semester.iterdir():
                folder_id = folder.name[:6]
                local_ids[folder_id] = folder.name
        return local_ids

    def find_missing_values(self):
        data = self.fetch_all()
        missing = {}
        
        for fid, entry in data.items():
            missing_keys = [
                key for key in ("text", "author", "keywords", "name", "semestr", "tags")
                if not entry.get(key)
            ]
            if missing_keys:
                missing[fid] = missing_keys

        for fid, keys in missing.items():
            logger.warning(f"{fid}: missing {keys}")
