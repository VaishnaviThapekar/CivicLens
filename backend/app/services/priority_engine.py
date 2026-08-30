"""
CivicLens Explainable Priority & Safety Risk Engine
Calculates Explainable Priority Score (0-100), 6 Safety Risk Types, Department Recommendation, and Ward/Zone Assignment.
"""

def calculate_explainable_priority(
  category: str,
  description: str = "",
  reports_count: int = 1,
  has_school_or_bus_stop: bool = True
) -> dict:
  desc_lower = description.lower()

  if any(w in desc_lower for w in ["pothole", "accident", "fall", "danger", "burst"]):
    safety_score = 30
  elif any(w in desc_lower for w in ["waterlogging", "garbage", "drain"]):
    safety_score = 22
  else:
    safety_score = 14

  if any(w in desc_lower for w in ["huge", "large", "crater", "overflow", "severe"]):
    severity_score = 25
  else:
    severity_score = 16

  reports_score = min(reports_count * 3, 15)

  if any(w in desc_lower for w in ["road", "bottleneck", "traffic", "underpass", "junction"]):
    traffic_score = 12
  else:
    traffic_score = 6

  if any(w in desc_lower for w in ["yesterday", "days", "persistent", "week"]):
    duration_score = 10
  else:
    duration_score = 6

  location_score = 8 if has_school_or_bus_stop else 5

  total_score = safety_score + severity_score + reports_score + traffic_score + duration_score + location_score

  if total_score >= 80:
    priority_level = "P1 — Critical"
    severity_label = "Critical"
  elif total_score >= 60:
    priority_level = "P2 — High"
    severity_label = "High"
  elif total_score >= 40:
    priority_level = "P3 — Medium"
    severity_label = "Medium"
  else:
    priority_level = "P4 — Low"
    severity_label = "Low"

  detected_risks = []
  if safety_score >= 25: detected_risks.append("Accident Risk")
  if has_school_or_bus_stop: detected_risks.append("Pedestrian Risk")
  if traffic_score >= 10: detected_risks.append("Traffic Risk")
  if "garbage" in desc_lower or "waste" in desc_lower: detected_risks.append("Health Risk")
  if "drain" in desc_lower or "waterlogging" in desc_lower: detected_risks.append("Flooding Risk")
  if "light" in desc_lower or "wiring" in desc_lower: detected_risks.append("Fire / Electrical Infrastructure Risk")

  dept = (
    "Municipal Road & Bridges Division (PWD)" if category in ["Road", "Potholes"]
    else "Water Supply & Maintenance Cell" if category in ["Water", "Water leakage"]
    else "Solid Waste Management & Sanitation" if category in ["Waste", "Garbage"]
    else "Stormwater Drainage & Sewerage" if category in ["Drainage", "Waterlogging"]
    else "Electrical Infrastructure Cell"
  )

  return {
    "total_score": total_score,
    "priority_level": priority_level,
    "severity_label": severity_label,
    "breakdown": {
      "safety_risk": safety_score,
      "severity": severity_score,
      "reports": reports_score,
      "traffic_impact": traffic_score,
      "duration": duration_score,
      "location": location_score
    },
    "detected_risks": detected_risks,
    "department_recommendation": dept,
    "ward_assignment": {
      "city": "Central District",
      "ward": "Ward 63",
      "zone": "Zone 4",
      "responsible_authority": "Executive Engineer R. K. Patil (PWD)"
    }
  }

# Alias for route modules
def calculate_priority_score(category: str, description: str = "", reports_count: int = 1) -> dict:
  res = calculate_explainable_priority(category, description, reports_count)
  return {
    "score": res["total_score"],
    "priority_level": res["priority_level"],
    "breakdown": res["breakdown"],
    "detected_risks": res["detected_risks"]
  }
