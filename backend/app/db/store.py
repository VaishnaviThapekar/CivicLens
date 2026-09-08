import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from app.models.schemas import Complaint, UserProfile

DATA_DIR = Path(__file__).parent.parent.parent / "data"
DB_FILE_PATH = DATA_DIR / "store.json"

class DataStore:
    def __init__(self, persistence_file: Path = DB_FILE_PATH):
        self.persistence_file = persistence_file
        self.complaints: Dict[str, Complaint] = {}
        self.users: Dict[str, UserProfile] = {}
        self.user_passwords: Dict[str, str] = {}
        self.tokens: Dict[str, Dict[str, Any]] = {}
        self.comments: Dict[str, List[Dict[str, Any]]] = {}
        self.attachments: Dict[str, List[Dict[str, Any]]] = {}
        self._load_from_disk()

    def _load_from_disk(self):
        """Loads serialized data collections from JSON file into memory on startup."""
        if not self.persistence_file.exists():
            return

        try:
            with open(self.persistence_file, "r", encoding="utf-8") as f:
                data = json.load(f)

                complaint_data = data.get("complaints", {})
                for cid, cdict in complaint_data.items():
                    try:
                        self.complaints[cid] = Complaint.model_validate(cdict)
                    except Exception:
                        self.complaints[cid] = Complaint(**cdict)

                user_data = data.get("users", {})
                for uid, udict in user_data.items():
                    try:
                        self.users[uid] = UserProfile.model_validate(udict)
                    except Exception:
                        self.users[uid] = UserProfile(**udict)

                self.user_passwords = data.get("user_passwords", {})
                self.tokens = data.get("tokens", {})
                self.comments = data.get("comments", {})
                self.attachments = data.get("attachments", {})

        except Exception as err:
            print(f"Warning: Failed to load data store from disk: {err}")

    def _save_to_disk(self):
        """Persists all active data collections to disk synchronously."""
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            serialized = {
                "complaints": {
                    cid: c.model_dump(mode="json") if hasattr(c, "model_dump") else c.dict()
                    for cid, c in self.complaints.items()
                },
                "users": {
                    uid: u.model_dump(mode="json") if hasattr(u, "model_dump") else u.dict()
                    for uid, u in self.users.items()
                },
                "user_passwords": self.user_passwords,
                "tokens": self.tokens,
                "comments": self.comments,
                "attachments": self.attachments
            }
            with open(self.persistence_file, "w", encoding="utf-8") as f:
                json.dump(serialized, f, indent=2, default=str)
        except Exception as err:
            print(f"Warning: Failed to save data store to disk: {err}")

    # Complaint operations
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

    # User operations
    def add_user(self, user: UserProfile, hashed_password: str = "") -> UserProfile:
        self.users[user.email] = user
        if hashed_password:
            self.user_passwords[user.email] = hashed_password
        self._save_to_disk()
        return user

    def get_user_by_email(self, email: str) -> Optional[UserProfile]:
        return self.users.get(email)

    def get_user_password(self, email: str) -> Optional[str]:
        return self.user_passwords.get(email)

    # Token operations
    def save_token(self, token: str, user_info: dict):
        self.tokens[token] = user_info
        self._save_to_disk()

    def get_token(self, token: str) -> Optional[dict]:
        return self.tokens.get(token)

    # Comment & Attachment operations (Bug 46 Fix)
    def add_comment(self, complaint_id: str, comment_entry: dict):
        if complaint_id not in self.comments:
            self.comments[complaint_id] = []
        self.comments[complaint_id].append(comment_entry)
        self._save_to_disk()

    def get_comments(self, complaint_id: str) -> List[dict]:
        return self.comments.get(complaint_id, [])

    def add_attachment(self, complaint_id: str, attachment_entry: dict):
        if complaint_id not in self.attachments:
            self.attachments[complaint_id] = []
        self.attachments[complaint_id].append(attachment_entry)
        self._save_to_disk()

    def get_attachments(self, complaint_id: str) -> List[dict]:
        return self.attachments.get(complaint_id, [])

    def clear(self):
        self.complaints.clear()
        self.users.clear()
        self.user_passwords.clear()
        self.tokens.clear()
        self.comments.clear()
        self.attachments.clear()
        self._save_to_disk()

db_store = DataStore()
