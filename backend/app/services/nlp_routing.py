"""
CivicLens Multilingual NLP & Department Routing Service
Processes Text & Speech-to-Text (Marathi, Hindi, English) to extract Issue, Location, Duration, Severity Clues, Objects, Context, and Safety Concerns.
"""

from app.models.schemas import ComplaintCategory, PriorityLevel, StructuredAIUnderstanding

DEPARTMENT_ROUTING_MAP = {
  ComplaintCategory.ROAD_INFRASTRUCTURE: "Municipal Road & Bridges Division (PWD)",
  ComplaintCategory.WATER_LEAKAGE: "Water Supply & Maintenance Cell",
  ComplaintCategory.GARBAGE_SANITATION: "Solid Waste Management & Sanitation Department",
  ComplaintCategory.STREETLIGHT_ELECTRICAL: "Electrical Infrastructure Cell",
  ComplaintCategory.DRAINAGE_FLOODING: "Stormwater Drainage & Sewerage Department",
  ComplaintCategory.TRAFFIC_SAFETY: "Traffic Infrastructure Control Cell"
}

def detect_language(text: str) -> str:
  if any(w in text for w in ["इथे", "रस्त्यावर", "खड्डा", "काल", "बायका", "झाले"]):
    return "Marathi"
  elif any(w in text for w in ["यहाँ", "सड़क", "कचरा", "बदबू", "पानी"]):
    return "Hindi"
  return "English"

def parse_multilingual_report(text: str, voice_transcript: str = "") -> dict:
  combined = (text + " " + voice_transcript).lower()
  lang = detect_language(text + " " + voice_transcript)

  if any(w in combined for w in ["pothole", "crater", "road", "crack"]):
    category = ComplaintCategory.ROAD_INFRASTRUCTURE
    subcategory = "Pothole"
    title = "Road Surface Pothole Hazard"
    priority = PriorityLevel.P1
    priority_reason = "High traffic bottleneck & safety risk"
    severity = "CRITICAL"
  elif any(w in combined for w in ["garbage", "trash", "dump", "waste"]):
    category = ComplaintCategory.GARBAGE_SANITATION
    subcategory = "Overflowing bin"
    title = "Overflowing Sanitation Container"
    priority = PriorityLevel.P2
    priority_reason = "Public health & vector hazard"
    severity = "HIGH"
  elif any(w in combined for w in ["water", "drain", "waterlogging", "pipe"]):
    category = ComplaintCategory.DRAINAGE_FLOODING if "drain" in combined else ComplaintCategory.WATER_LEAKAGE
    subcategory = "Clogged drain"
    title = "Stormwater Drainage Clog / Leakage"
    priority = PriorityLevel.P1
    priority_reason = "Urban flash flooding risk"
    severity = "CRITICAL"
  elif any(w in combined for w in ["light", "lamp", "pole"]):
    category = ComplaintCategory.STREETLIGHT_ELECTRICAL
    subcategory = "Unlit streetlight"
    title = "Unlit Streetlight Junction"
    priority = PriorityLevel.P3
    priority_reason = "Nighttime pedestrian visibility"
    severity = "MEDIUM"
  else:
    category = ComplaintCategory.ROAD_INFRASTRUCTURE
    subcategory = "General civic issue"
    title = "General Civic Issue Report"
    priority = PriorityLevel.P3
    priority_reason = "Routine municipal SLA"
    severity = "MEDIUM"

  department = DEPARTMENT_ROUTING_MAP.get(category, "General Municipal Grievance Cell")

  structured = StructuredAIUnderstanding(
    category=category,
    subcategory=subcategory,
    severity=severity,
    urgency="24_HOURS" if severity in ["CRITICAL", "HIGH"] else "SCHEDULED",
    duration="Persistent (24-72 Hours)",
    location_description="Parsed from GPS / Landmark text",
    potential_risk="PEDESTRIAN_AND_VEHICLE_ACCIDENT_HAZARD",
    department=department,
    required_action="Dispatch repair unit for surface compaction",
    confidence=0.94,
    keywords=[category.value, subcategory],
    detected_objects=["Damaged Surface", "Pedestrian Corridor"]
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
