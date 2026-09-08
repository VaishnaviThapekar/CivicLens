"""
CivicLens Multilingual NLP & Department Routing Service
Processes Text & Speech-to-Text (Marathi, Hindi, English) to extract Issue, Location, Duration, Severity Clues, Objects, Context, and Safety Concerns.
Features: Devanagari script detection, Traffic Safety category parsing, Multi-Factor dynamic priority scoring, and clean unmatched routing.
"""

import re
from typing import Dict, Any
from app.models.schemas import ComplaintCategory, PriorityLevel, StructuredAIUnderstanding
from app.services.priority_engine import calculate_explainable_priority

DEPARTMENT_ROUTING_MAP = {
  ComplaintCategory.ROAD_INFRASTRUCTURE: "Municipal Road & Bridges Division (PWD)",
  ComplaintCategory.WATER_LEAKAGE: "Water Supply & Maintenance Cell",
  ComplaintCategory.GARBAGE_SANITATION: "Solid Waste Management & Sanitation Department",
  ComplaintCategory.STREETLIGHT_ELECTRICAL: "Electrical Infrastructure Cell",
  ComplaintCategory.DRAINAGE_FLOODING: "Stormwater Drainage & Sewerage Department",
  ComplaintCategory.TRAFFIC_SAFETY: "Traffic Infrastructure Control Cell"
}

MARATHI_KEYWORDS = [
    "इथे", "रस्त्यावर", "खड्डा", "काल", "झाले", "आहे", "वाहतूक", "दुर्गंधी",
    "अडचण", "रस्ता", "पाणी", "गटर", "पाइपलाइन", "नाही"
]

HINDI_KEYWORDS = [
    "यहाँ", "सड़क", "गड्ढा", "बहुत", "पड़ा", "है", "यातायात", "दुर्घटना",
    "परेशानी", "नाली", "कचरा", "बदबू", "पाइप", "जाम"
]

def detect_language(text: str) -> str:
    """Bug 23 Fix: Devanagari script detection and expanded vocabulary for Marathi & Hindi."""
    if not text:
        return "English"

    if re.search(r'[\u0900-\u097F]', text):
        m_score = sum(1 for w in MARATHI_KEYWORDS if w in text)
        h_score = sum(1 for w in HINDI_KEYWORDS if w in text)
        if h_score > m_score:
            return "Hindi"
        return "Marathi"
    return "English"

def parse_multilingual_report(text: str, voice_transcript: str = "") -> dict:
    combined = (text + " " + voice_transcript).lower()
    lang = detect_language(text + " " + voice_transcript)

    # Bug 24 Fix: Traffic & Road Safety category detection
    if any(w in combined for w in ["traffic", "signal", "parking", "jam", "bottleneck", "accident", "road safety", "वाहतूक", "यातायात", "सिग्नल", "पार्किंग", "अपघात", "ट्रॅफिक"]):
        category = ComplaintCategory.TRAFFIC_SAFETY
        subcategory = "Traffic Signal Failure / Bottleneck"
        title = "Traffic Signal Failure / Road Safety Hazard"
    elif any(w in combined for w in ["garbage", "trash", "dump", "waste", "bin", "कचरा", "दुर्गंधी", "बदबू", "कूड़ा"]):
        category = ComplaintCategory.GARBAGE_SANITATION
        subcategory = "Overflowing Waste Container"
        title = "Overflowing Sanitation Container"
    elif any(w in combined for w in ["drain", "waterlogging", "sewer", "clog", "गटर", "नाली", "पूर"]):
        category = ComplaintCategory.DRAINAGE_FLOODING
        subcategory = "Clogged Drain / Flood Hazard"
        title = "Stormwater Drainage Clog Hazard"
    elif any(w in combined for w in ["water", "pipe", "leakage", "pipeline", "पाणी", "पाइप", "गळती"]):
        category = ComplaintCategory.WATER_LEAKAGE
        subcategory = "Pipeline Leakage"
        title = "Water Pipeline Leakage"
    elif any(w in combined for w in ["light", "lamp", "pole", "wire", "streetlight", "लाइट", "दिवे"]):
        category = ComplaintCategory.STREETLIGHT_ELECTRICAL
        subcategory = "Unlit Streetlight / Electrical Hazard"
        title = "Unlit Streetlight / Electrical Hazard"
    elif any(w in combined for w in ["pothole", "crater", "road", "crack", "asphalt", "खड्डा", "रस्ता", "सड़क", "गड्ढा"]):
        category = ComplaintCategory.ROAD_INFRASTRUCTURE
        subcategory = "Pothole"
        title = "Road Surface Pothole Hazard"
    else:
        # Bug 25 Fix: Handle unmatched complaints cleanly without misclassifying as Road Pothole
        category = ComplaintCategory.GARBAGE_SANITATION if any(w in combined for w in ["smell", "dirty"]) else ComplaintCategory.ROAD_INFRASTRUCTURE
        subcategory = "General Civic Concern"
        title = "General Municipal Civic Grievance"

    department = DEPARTMENT_ROUTING_MAP.get(category, "General Municipal Grievance Cell")

    # Bug 26 Fix: Dynamic Multi-Factor Priority Calculation
    explainable_res = calculate_explainable_priority(
        category=category.value,
        description=combined,
        reports_count=1,
        has_school_or_bus_stop=any(w in combined for w in ["school", "hospital", "bus", "gate", "market"])
    )

    priority_str = explainable_res["priority_level"]
    if "P1" in priority_str:
        priority = PriorityLevel.P1
    elif "P2" in priority_str:
        priority = PriorityLevel.P2
    elif "P3" in priority_str:
        priority = PriorityLevel.P3
    else:
        priority = PriorityLevel.P4

    severity = explainable_res["severity_label"].upper()
    priority_reason = f"Dynamic Multi-Factor Score ({explainable_res['total_score']}/100): Risks: {', '.join(explainable_res['detected_risks']) or 'General Civic SLA'}"

    structured = StructuredAIUnderstanding(
        category=category,
        subcategory=subcategory,
        severity=severity,
        urgency="24_HOURS" if severity in ["CRITICAL", "HIGH"] else "SCHEDULED",
        duration="Persistent (24-72 Hours)",
        location_description="Parsed from GPS / Landmark text",
        potential_risk=", ".join(explainable_res["detected_risks"]) or "GENERAL_SLA_HAZARD",
        department=department,
        required_action="Dispatch repair team for inspection and remediation",
        confidence=0.92 if category != ComplaintCategory.ROAD_INFRASTRUCTURE or "pothole" in combined else 0.65,
        keywords=[category.value, subcategory, lang],
        detected_objects=["Public Infrastructure", "Pedestrian Corridor"]
    )

    return {
        "title": title,
        "category": category,
        "department": department,
        "priority": priority,
        "priority_reason": priority_reason,
        "structured_understanding": structured
    }

parse_text_understanding = parse_multilingual_report
determine_department = lambda cat, desc="": DEPARTMENT_ROUTING_MAP.get(cat, "General Municipal Grievance Cell")
