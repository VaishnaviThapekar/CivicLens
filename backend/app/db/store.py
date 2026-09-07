import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from app.models.schemas import Complaint

DATA_DIR = Path(__file__).parent.parent.parent / "data"
DB_FILE_PATH = DATA_DIR / "store.json"

class DataStore:
    def __init__(self, persistence_file: Path = DB_FILE_PATH):
        self.persistence_file = persistence_file
        self.complaints: Dict[str, Complaint] = {}
        self._load_from_disk()

    def _load_from_disk(self):
        """Loads serialized complaints from JSON file into memory on startup."""
        if not self.persistence_file.exists():
            return

        try:
            with open(self.persistence_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for cid, complaint_dict in data.items():
                    try:
                        self.complaints[cid] = Complaint.model_validate(complaint_dict)
                    except Exception as e:
                        # Fallback for dict instantiation if pydantic v1 vs v2
                        self.complaints[cid] = Complaint(**complaint_dict)
        except Exception as err:
            print(f"Warning: Failed to load complaints from disk persistence file: {err}")

    def _save_to_disk(self):
        """Persists all active complaints to disk synchronously."""
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            serialized = {
                cid: c.model_dump(mode="json") if hasattr(c, "model_dump") else c.dict()
                for cid, c in self.complaints.items()
            }
            with open(self.persistence_file, "w", encoding="utf-8") as f:
                json.dump(serialized, f, indent=2, default=str)
        except Exception as err:
            print(f"Warning: Failed to save complaints to disk persistence file: {err}")

    def get_all_complaints(self) -> List[Complaint]:
        return list(self.complaints.values())

    def get_complaint_by_id(self, complaint_id: str) -> Optional[Complaint]:
        return self.complaints.get(complaint_id)

    def add_complaint(self, complaint: Complaint) -> Complaint:
        self.complaints[complaint.id] = complaint
        self._save_to_disk()
        return complaint

    def update_complaint(self, complaint: Complaint) -> Complaint:
        self.complaints[complaint.id] = complaint
        self._save_to_disk()
        return complaint

    def delete_complaint(self, complaint_id: str) -> bool:
        if complaint_id in self.complaints:
            del self.complaints[complaint_id]
            self._save_to_disk()
            return True
        return False

    def clear(self):
        self.complaints.clear()
        self._save_to_disk()

db_store = DataStore()
