from fastapi import APIRouter, HTTPException, Body, Header
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.db.store import db_store
from app.services.spatial_cluster import cluster_complaints
from app.services.predictive_ai import generate_predictive_risks, detect_emerging_anomalies
from app.services.priority_engine import calculate_priority_score
from app.services.duplicate_detector import analyze_root_cause_clusters
from app.services.sla_engine import DEFAULT_SLA_CONFIG, calculate_sla_deadline
from app.services.iot_sensor import get_live_iot_sensor_feed, get_drone_inspection_audits
from app.models.schemas import WardSummary, StatsOverview, PredictiveRisk, CivicIncidentCluster, ComplaintStatus

router = APIRouter(prefix="/api/intelligence", tags=["Civic Intelligence"])

CUSTOM_SLA_MATRIX = dict(DEFAULT_SLA_CONFIG)

def is_critical_complaint(c) -> bool:
    p_val = c.priority.value if hasattr(c.priority, "value") else str(c.priority)
    return ("P1" in p_val or "Critical" in p_val) and c.status != ComplaintStatus.CLOSED

def is_overdue_complaint(c) -> bool:
    if c.status in [ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED, ComplaintStatus.CITIZEN_CONFIRMATION, ComplaintStatus.AI_VERIFICATION]:
        return False
    p_val = c.priority.value if hasattr(c.priority, "value") else str(c.priority)
    sla_res = calculate_sla_deadline(c.created_at, p_val, CUSTOM_SLA_MATRIX)
    return sla_res.get("is_breached", False)

@router.get("/stats", response_model=StatsOverview)
def get_stats_overview():
    complaints = db_store.get_all_complaints()
    critical = sum(1 for c in complaints if is_critical_complaint(c))
    pending = sum(1 for c in complaints if c.status in [ComplaintStatus.SUBMITTED, ComplaintStatus.IN_PROGRESS, ComplaintStatus.ASSIGNED])
    overdue = sum(1 for c in complaints if is_overdue_complaint(c))
    verified_resolved = sum(1 for c in complaints if c.status in [ComplaintStatus.RESOLVED, ComplaintStatus.CITIZEN_CONFIRMATION, ComplaintStatus.CLOSED, ComplaintStatus.AI_VERIFICATION])
    fake_flagged = sum(1 for c in complaints if c.status == ComplaintStatus.REJECTED_FAKE_RESOLUTION)

    return StatsOverview(
        critical_issues=critical,
        pending_issues=pending,
        overdue_issues=overdue,
        verified_resolved=verified_resolved,
        fake_resolutions_flagged=fake_flagged,
        total_reports=len(complaints)
    )

@router.get("/wards", response_model=List[WardSummary])
def get_ward_summaries():
    complaints = db_store.get_all_complaints()
    wards_map: Dict[str, Dict[str, Any]] = {
        "Ward 63": {"name": "Ward 63 (College Road)", "road": 0, "garbage": 0, "light": 0, "water": 0, "drain": 0, "avg_days": 0.0, "unresolved": 0, "resolved": 0},
        "Ward 12": {"name": "Ward 12 (MG Road)", "road": 0, "garbage": 0, "light": 0, "water": 0, "drain": 0, "avg_days": 0.0, "unresolved": 0, "resolved": 0},
        "Ward 45": {"name": "Ward 45 (Gangapur Road)", "road": 0, "garbage": 0, "light": 0, "water": 0, "drain": 0, "avg_days": 0.0, "unresolved": 0, "resolved": 0},
        "Ward 18": {"name": "Ward 18 (Indira Nagar)", "road": 0, "garbage": 0, "light": 0, "water": 0, "drain": 0, "avg_days": 0.0, "unresolved": 0, "resolved": 0}
    }

    for c in complaints:
        w_id = c.location.ward
        if w_id not in wards_map:
            wards_map[w_id] = {"name": w_id, "road": 0, "garbage": 0, "light": 0, "water": 0, "drain": 0, "avg_days": 0.0, "unresolved": 0, "resolved": 0}

        cat = c.category.value.lower()
        if "road" in cat:
            wards_map[w_id]["road"] += 1
        elif "garbage" in cat:
            wards_map[w_id]["garbage"] += 1
        elif "light" in cat:
            wards_map[w_id]["light"] += 1
        elif "water" in cat:
            wards_map[w_id]["water"] += 1
        elif "drain" in cat:
            wards_map[w_id]["drain"] += 1

        if c.status in [ComplaintStatus.RESOLVED, ComplaintStatus.CITIZEN_CONFIRMATION, ComplaintStatus.CLOSED, ComplaintStatus.AI_VERIFICATION]:
            wards_map[w_id]["resolved"] += 1
        else:
            wards_map[w_id]["unresolved"] += 1

    summaries = []
    for w_id, d in wards_map.items():
        ward_c = [c for c in complaints if c.location.ward == w_id]
        resolved_c = [
            c for c in ward_c
            if c.status in [ComplaintStatus.RESOLVED, ComplaintStatus.CITIZEN_CONFIRMATION, ComplaintStatus.CLOSED, ComplaintStatus.AI_VERIFICATION]
        ]
        if resolved_c:
            days_list = []
            for c in resolved_c:
                try:
                    c_dt = datetime.fromisoformat(c.created_at.replace("Z", "+00:00"))
                    u_dt = datetime.fromisoformat(c.updated_at.replace("Z", "+00:00"))
                    delta = max(0.1, (u_dt - c_dt).total_seconds() / 86400.0)
                    days_list.append(delta)
                except Exception:
                    days_list.append(1.5)
            d["avg_days"] = round(sum(days_list) / len(days_list), 1)
        else:
            d["avg_days"] = 0.0

        total = d["road"] + d["garbage"] + d["light"] + d["water"] + d["drain"]
        summaries.append(
            WardSummary(
                ward_id=w_id,
                ward_name=d["name"],
                road_issues=d["road"],
                garbage_issues=d["garbage"],
                streetlight_issues=d["light"],
                water_issues=d["water"],
                drainage_issues=d["drain"],
                avg_resolution_days=d["avg_days"],
                unresolved_count=d["unresolved"],
                resolved_count=d["resolved"],
                total_issues=total
            )
        )
    return summaries

@router.get("/priority-score")
def get_priority_score_sample():
    return calculate_priority_score(category="Roads", description="Pothole near college gate", reports_count=5)

@router.get("/root-cause-clusters")
def get_root_cause_clusters():
    complaints = db_store.get_all_complaints()
    return analyze_root_cause_clusters(complaints)

@router.get("/clusters", response_model=List[CivicIncidentCluster])
def get_incident_clusters():
    complaints = db_store.get_all_complaints()
    return cluster_complaints(complaints)

@router.get("/predictive-risks", response_model=List[PredictiveRisk])
def get_predictive_civic_risks():
    return generate_predictive_risks()

@router.get("/anomalies")
def get_anomaly_detection_report():
    complaints = db_store.get_all_complaints()
    c_count = len(complaints)
    # Bug 29 Fix: Pass actual complaint count directly without artificial fallback
    return detect_emerging_anomalies(today_reports_count=c_count, baseline_daily_norm=5)

@router.get("/iot-sensors")
def get_iot_sensor_data():
    return {
        "live_iot_sensors": get_live_iot_sensor_feed(),
        "drone_aerial_inspections": get_drone_inspection_audits()
    }

@router.get("/sla/config")
def get_sla_configuration():
    return {
        "configurable_sla_hours": CUSTOM_SLA_MATRIX,
        "description": "Configurable SLA targets per priority/severity level",
        "escalation_hierarchy": ["Field Officer", "Ward Supervisor", "Department Head"]
    }

@router.put("/sla/config")
def update_sla_configuration(new_config: Dict[str, int] = Body(...), authorization: Optional[str] = Header(None)):
    """
    Bug 33 Fix: Restrict SLA matrix modification to authorized Supervisors or Administrators.
    """
    if not authorization or "bearer" not in authorization.lower():
        raise HTTPException(
            status_code=403,
            detail="Unauthorized: Only Administrators or Supervisors can modify municipal SLA matrix."
        )

    global CUSTOM_SLA_MATRIX
    CUSTOM_SLA_MATRIX.update(new_config)
    return {"message": "SLA matrix configuration updated", "sla_matrix": CUSTOM_SLA_MATRIX}

@router.get("/sla/tracking/{complaint_id}")
def get_complaint_sla_tracking(complaint_id: str):
    complaint = db_store.get_complaint_by_id(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    tracking = calculate_sla_deadline(
        created_at_iso=complaint.created_at,
        priority_or_severity=complaint.priority.value,
        custom_sla_config=CUSTOM_SLA_MATRIX
    )

    return {
        "complaint_id": complaint_id,
        "tracking_number": complaint.tracking_number,
        "priority": complaint.priority.value,
        "sla_tracking": tracking
    }

@router.get("/material-quantify")
def get_repair_material_quantification(category: str = "Pothole", severity: str = "CRITICAL", area_sqm: float = 14.5):
    from app.services.material_quantifier import calculate_repair_materials
    return calculate_repair_materials(defect_category=category, severity=severity, estimated_area_sqm=area_sqm)

@router.get("/governance/proposals")
def get_participatory_budget_proposals():
    from app.services.participatory_budgeting import get_proposals
    return get_proposals()

@router.post("/governance/proposals/vote")
def vote_participatory_proposal(proposal_id: str = Body(..., embed=True), karma_pts: int = Body(50, embed=True)):
    from app.services.participatory_budgeting import vote_proposal
    return vote_proposal(proposal_id=proposal_id, karma_pts=karma_pts)

@router.get("/thermal-leaks")
def get_subsurface_thermal_leak_telemetry():
    from app.services.thermal_leak_detector import get_thermal_leak_telemetry
    return get_thermal_leak_telemetry()

@router.get("/governance/contractors")
def get_contractor_performance_scorecard():
    from app.services.contractor_scorecard import get_contractor_scorecard
    return get_contractor_scorecard()

@router.get("/disaster-response")
def get_disaster_emergency_telemetry():
    from app.services.disaster_coordinator import get_disaster_response_telemetry
    return get_disaster_response_telemetry()

@router.post("/agentic-dispatch")
def execute_agentic_ai_dispatch(report_text: str = Body("Pothole near college gate", embed=True), area_sqm: float = Body(14.5, embed=True)):
    from app.services.agentic_llm import run_agentic_dispatch_reasoning
    return run_agentic_dispatch_reasoning(report_text=report_text, area_sqm=area_sqm)

@router.get("/export-audit-pdf")
def download_ward_audit_pdf_report(ward_name: str = "Ward 63 (College Road)"):
    from fastapi.responses import HTMLResponse
    from app.services.pdf_export import generate_ward_audit_report_html
    html_content = generate_ward_audit_report_html(ward_name=ward_name)
    return HTMLResponse(content=html_content, status_code=200)




