from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class Role(str, Enum):
    CITIZEN = "Citizen"
    VOLUNTEER = "Volunteer"
    OFFICER = "Officer"
    SUPERVISOR = "Supervisor"
    ADMINISTRATOR = "Administrator"
    ANALYST = "Analyst"

class ComplaintCategory(str, Enum):
    ROAD_INFRASTRUCTURE = "Road Infrastructure"
    GARBAGE_SANITATION = "Garbage & Sanitation"
    STREETLIGHT_ELECTRICAL = "Streetlight & Electrical"
    WATER_LEAKAGE = "Water Supply & Leakage"
    DRAINAGE_FLOODING = "Drainage & Waterlogging"
    TRAFFIC_SAFETY = "Traffic & Road Safety"

class PriorityLevel(str, Enum):
    P1 = "P1 — Critical"
    P2 = "P2 — High"
    P3 = "P3 — Medium"
    P4 = "P4 — Low"

class ComplaintStatus(str, Enum):
    SUBMITTED = "Submitted"
    AI_ANALYSIS = "AI Analysis Completed"
    VERIFIED = "AI Verified Defect"
    ASSIGNED = "Assigned to Department"
    IN_PROGRESS = "Work in Progress"
    RESOLVED = "Resolved (Pending Verification)"
    AI_VERIFICATION = "AI Verification Passed"
    CITIZEN_CONFIRMATION = "Citizen Confirmed"
    CLOSED = "Closed"
    REOPENED = "Reopened (Not Fixed)"
    REJECTED = "Rejected"
    REJECTED_FAKE_RESOLUTION = "Fake Resolution Flagged"

class SmartTicket(BaseModel):
    ticket_id: str  # e.g., CL-2026-001482
    issue_title: str
    category: ComplaintCategory
    subcategory: str
    severity: PriorityLevel
    location_summary: str
    assigned_department: str
    assigned_officer: str
    sla_deadline: str
    estimated_resolution_days: float
    status: ComplaintStatus
    resolution_confidence_percent: Optional[float] = None
    human_review_triggered: bool = False

class UserProfile(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    role: Role = Role.CITIZEN
    language_preference: str = "en"  # en, hi, mr
    avatar_url: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class LocationData(BaseModel):
    lat: float
    lng: float
    address: str = "Unspecified Location"
    city: str = "Nashik"
    ward: str = "Ward 63"
    zone: str = "Zone 4"
    road_name: str = "College Road Main Line"
    nearest_landmark: str = "Near City Campus Gate 2"
    postgis_geometry: str = "ST_SetSRID(ST_Point(73.7898, 19.9975), 4326)"

class AIDetectionDetails(BaseModel):
    object_detected: str
    confidence: float  # e.g., 0.96
    estimated_dimensions: str  # e.g., "1.8m × 0.9m"
    estimated_area_m2: float = 1.8  # e.g., 1.8 m²
    road_obstruction: str = "Partial Lane Obstruction"
    risk_level: str = "HIGH"
    visual_summary: str
    detected_bboxes: List[Dict[str, Any]] = Field(default_factory=list)

class StructuredAIUnderstanding(BaseModel):
    category: ComplaintCategory
    subcategory: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    urgency: str   # IMMEDIATE, 24_HOURS, SCHEDULED
    duration: str  # e.g. "~1 day"
    location_description: str
    potential_risk: str
    department: str
    required_action: str
    confidence: float
    keywords: List[str] = Field(default_factory=list)
    detected_objects: List[str] = Field(default_factory=list)

class ResolutionVerificationResult(BaseModel):
    complaint_id: str
    claimed_resolution: bool = True
    visual_evidence_valid: bool = True
    ai_verification_score: float = 0.0  # 0 to 100%
    image_match_percentage: float = 0.0  # e.g. 32%
    gps_consistency: str = "HIGH"        # HIGH, LOW, MISMATCHED
    timestamp_freshness: str = "RECENT"  # RECENT, UNKNOWN, STALE
    environment_context_match: str = "VERIFIED" # VERIFIED, INCONSISTENT
    human_review_triggered: bool = False
    citizen_confirmation: str = "PENDING"  # PENDING, CONFIRMED, DISPUTED
    fake_resolution_detected: bool = False
    confidence: float = 0.0
    match_analysis: Dict[str, Any] = Field(default_factory=dict)
    message: str = ""
    verified_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class ComplaintCreate(BaseModel):
    title: Optional[str] = None
    description: str
    media_type: str = "image"  # image, video, voice, text
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    voice_transcript: Optional[str] = None
    audio_base64: Optional[str] = None
    language: str = "en"
    location: LocationData

class Complaint(BaseModel):
    id: str
    tracking_number: str
    title: str
    description: str
    media_type: str = "image"
    category: ComplaintCategory
    department: str = "Municipal Road & Bridges Division"
    priority: PriorityLevel
    priority_reason: str
    status: ComplaintStatus
    location: LocationData
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    voice_transcript: Optional[str] = None
    ai_detection: Optional[AIDetectionDetails] = None
    structured_understanding: Optional[StructuredAIUnderstanding] = None
    cluster_id: Optional[str] = None
    submitted_by: str = "Citizen"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    officer_assigned: Optional[str] = None
    resolution_evidence_image_url: Optional[str] = None
    resolution_officer_notes: Optional[str] = None
    verification_result: Optional[ResolutionVerificationResult] = None

class CivicIncidentCluster(BaseModel):
    cluster_id: str
    title: str
    category: ComplaintCategory
    ward: str
    latitude: float
    longitude: float
    radius_meters: float = 500.0
    supporting_reports_count: int
    report_ids: List[str]
    status: str = "Active"
    priority: PriorityLevel
    created_at: str

class PredictiveRisk(BaseModel):
    id: str
    zone: str
    ward: str
    hazard_type: str
    probability: float
    risk_level: str
    trigger_factors: List[str]
    recommended_action: str
    historical_correlation: str

class WardSummary(BaseModel):
    ward_id: str
    ward_name: str
    road_issues: int
    garbage_issues: int
    streetlight_issues: int
    water_issues: int
    drainage_issues: int
    avg_resolution_days: float
    unresolved_count: int
    resolved_count: int
    total_issues: int

class StatsOverview(BaseModel):
    critical_issues: int
    pending_issues: int
    overdue_issues: int
    verified_resolved: int
    fake_resolutions_flagged: int
    total_reports: int
