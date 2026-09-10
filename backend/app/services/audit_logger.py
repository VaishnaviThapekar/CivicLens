"""
CivicLens Centralized Immutable Audit Trail Service
Records administrative, supervisor, officer, and citizen actions into persistent audit logs.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
from app.db.store import db_store

def log_audit_event(
    actor: str,
    action: str,
    complaint_id: str,
    actor_role: str = "System",
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
    reason: Optional[str] = None,
    ip_address: Optional[str] = "127.0.0.1"
) -> Dict[str, Any]:
    """
    Bug 33 Fix: Immutable audit trail logger for municipal actions.
    """
    entry = {
        "event_id": f"audit-{uuid.uuid4().hex[:8]}",
        "actor": actor,
        "actor_role": actor_role,
        "action": action,
        "complaint_id": complaint_id,
        "old_value": old_value,
        "new_value": new_value,
        "reason": reason or f"{action} executed by {actor}",
        "timestamp": datetime.now().isoformat(),
        "ip_address": ip_address
    }
    db_store.add_audit_log(entry)
    return entry

def get_audit_logs(complaint_id: Optional[str] = None) -> List[Dict[str, Any]]:
    return db_store.get_audit_logs(complaint_id)
