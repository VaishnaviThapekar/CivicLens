from typing import List, Dict, Optional
from app.models.schemas import Complaint

class DataStore:
    def __init__(self):
        # Clean, empty database store with zero pre-loaded dummy data
        self.complaints: Dict[str, Complaint] = {}

    def get_all_complaints(self) -> List[Complaint]:
        return list(self.complaints.values())

    def get_complaint_by_id(self, complaint_id: str) -> Optional[Complaint]:
        return self.complaints.get(complaint_id)

    def add_complaint(self, complaint: Complaint) -> Complaint:
        self.complaints[complaint.id] = complaint
        return complaint

    def update_complaint(self, complaint: Complaint) -> Complaint:
        self.complaints[complaint.id] = complaint
        return complaint

    def clear(self):
        self.complaints.clear()

db_store = DataStore()
