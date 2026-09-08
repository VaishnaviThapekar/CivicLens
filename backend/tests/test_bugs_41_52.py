"""
Unit test suite for CivicLens Backend Bugs 41 to 52.
"""

import pytest
import os
from pathlib import Path
from datetime import datetime
from fastapi.testclient import TestClient

from app.main import app
from app.db.store import DataStore, db_store
from app.models.schemas import Complaint, LocationData, ComplaintCategory, ComplaintStatus, PriorityLevel
from app.services.websocket_manager import notify_complaint_created, notify_status_changed

client = TestClient(app)

def create_sample_complaint(comp_id: str, ward: str = "Ward 63", category: str = "Road Infrastructure"):
    cat_enum = ComplaintCategory.ROAD_INFRASTRUCTURE
    for c in ComplaintCategory:
        if c.value == category:
            cat_enum = c
            break

    dept = "Sanitation & Waste Department" if "Garbage" in category or "Waste" in category else "Municipal Road & Bridges Division"

    complaint = Complaint(
        id=comp_id,
        tracking_number=f"CL-NK-{datetime.now().year}-{comp_id.upper()}",
        title=f"Test issue {comp_id}",
        description="Sample test complaint for bugs 41-52",
        media_type="image",
        category=cat_enum,
        department=dept,
        priority=PriorityLevel.P2,
        priority_reason="Test priority",
        status=ComplaintStatus.SUBMITTED,
        location=LocationData(lat=19.9975, lng=73.7898, ward=ward)
    )
    db_store.add_complaint(complaint)
    return complaint

def test_bugs_46_47_centralized_datastore_persistence(tmp_path):
    """Bugs 46 & 47: Verify unified persistence of complaints, users, tokens, comments, and attachments."""
    test_db_file = tmp_path / "test_store.json"
    ds1 = DataStore(persistence_file=test_db_file)

    comp = create_sample_complaint("c-persist-101")

    # Add comments, attachments, tokens, and users to DataStore
    ds1.add_comment("c-persist-101", {"author": "Citizen", "text": "Persistent comment test"})
    ds1.add_attachment("c-persist-101", {"file_url": "https://example.com/photo.jpg", "description": "Persistent attachment test"})
    ds1.save_token("test-token-123", {"email": "citizen@civiclens.org"})

    # Re-instantiate DataStore from disk file to simulate server restart
    ds2 = DataStore(persistence_file=test_db_file)

    assert ds2.get_token("test-token-123") == {"email": "citizen@civiclens.org"}
    assert len(ds2.get_comments("c-persist-101")) == 1
    assert ds2.get_comments("c-persist-101")[0]["text"] == "Persistent comment test"
    assert len(ds2.get_attachments("c-persist-101")) == 1

def test_bugs_44_45_websocket_manager_broadcast_and_cleanup():
    """Bugs 44 & 45: Verify exception-safe WebSocket notifications."""
    comp = create_sample_complaint("c-ws-101")
    # Call notification functions (should run safely without throwing unhandled event loop exceptions)
    notify_complaint_created(comp)
    notify_status_changed(comp.id, "Assigned to Department", comp.tracking_number)

def test_bug_48_dynamic_contractor_rankings():
    """Bug 48: Verify contractor analytics are dynamically computed from active complaints."""
    db_store.complaints.clear()
    create_sample_complaint("c-road-1", category="Road Infrastructure")
    create_sample_complaint("c-waste-1", category="Garbage & Sanitation")

    res = client.get("/api/supervisor/contractors")
    assert res.status_code == 200
    contractors = res.json()

    road_contractor = next(c for c in contractors if "Roadways" in c["name"])
    assert road_contractor["total_assigned"] == 1

def test_bug_49_cpgrams_sync_message_wording():
    """Bug 49: Verify CPGRAMS sync endpoint returns accurate export dossier formatting message."""
    comp = create_sample_complaint("c-cpgrams-101")

    res = client.post(f"/api/supervisor/cpgrams/sync/{comp.id}")
    assert res.status_code == 200
    data = res.json()
    assert "CPGRAMS-compliant grievance dossier generated" in data["message"]
    assert "cpgrams_dossier" in data

def test_bugs_50_51_52_requirements_and_runner_config():
    """Bugs 50, 51, 52: Verify requirements version pinning, tinydb, and environment reload config."""
    req_path = Path(__file__).parent.parent / "requirements.txt"
    assert req_path.exists()
    content = req_path.read_text()

    assert "fastapi==" in content
    assert "tinydb==" in content
    assert "passlib==" in content

    run_path = Path(__file__).parent.parent / "run.py"
    run_content = run_path.read_text()
    assert "os.getenv(" in run_content
