"""
CivicLens Configurable SLA Engine & Breach Escalation Pipeline
Calculates real-time SLA deadlines, remaining time countdowns, multi-tier escalation stages (Officer -> Supervisor -> Department Head), and automated notifications.
"""

from datetime import datetime, timedelta
from typing import Dict, Any

# Configurable SLA matrix (in hours)
DEFAULT_SLA_CONFIG = {
  "Critical": 4,      # 4 Hours
  "P1 — Critical": 4,
  "High": 24,         # 24 Hours
  "P2 — High": 24,
  "Medium": 72,       # 3 Days (72 Hours)
  "P3 — Medium": 72,
  "Low": 168,         # 7 Days (168 Hours)
  "P4 — Low": 168
}

def calculate_sla_deadline(created_at_iso: str, priority_or_severity: str, custom_sla_config: Dict[str, int] = None) -> dict:
  """
  Calculates SLA deadline timestamp and remaining time.
  """
  sla_config = custom_sla_config or DEFAULT_SLA_CONFIG
  hours = sla_config.get(priority_or_severity, 24)

  try:
    created_dt = datetime.fromisoformat(created_at_iso.replace("Z", "+00:00"))
  except Exception:
    created_dt = datetime.now()

  deadline_dt = created_dt + timedelta(hours=hours)
  now_dt = datetime.now(created_dt.tzinfo)

  diff = deadline_dt - now_dt
  total_seconds = diff.total_seconds()

  is_breached = total_seconds < 0
  abs_seconds = abs(total_seconds)

  hours_rem = int(abs_seconds // 3600)
  mins_rem = int((abs_seconds % 3600) // 60)

  total_sla_seconds = hours * 3600.0
  elapsed_pct = round(((total_sla_seconds - total_seconds) / float(total_sla_seconds)) * 100.0, 1) if not is_breached else 100.0
  is_near_breach = not is_breached and elapsed_pct >= 80.0

  if is_breached:
    time_display = f"⚠️ SLA Breached by {hours_rem}h {mins_rem}m"
    if hours_rem >= 48:
      escalation_stage = "TIER_3_DEPARTMENT_HEAD"
      notified_roles = ["Officer", "Supervisor", "Department Head"]
    elif hours_rem >= 24:
      escalation_stage = "TIER_2_SUPERVISOR"
      notified_roles = ["Officer", "Supervisor"]
    else:
      escalation_stage = "TIER_1_OFFICER"
      notified_roles = ["Officer"]
  elif is_near_breach:
    time_display = f"⚠️ SLA Warning (80% Elapsed) — {hours_rem}h {mins_rem}m remaining"
    escalation_stage = "NEAR_BREACH_WARNING"
    notified_roles = ["Officer", "Supervisor"]
  else:
    time_display = f"⏳ {hours_rem}h {mins_rem}m remaining"
    escalation_stage = "NORMAL_SLA"
    notified_roles = []

  return {
    "sla_hours_assigned": hours,
    "deadline_timestamp": deadline_dt.isoformat(),
    "is_breached": is_breached,
    "is_near_breach": is_near_breach,
    "elapsed_percentage": max(0.0, min(100.0, elapsed_pct)),
    "time_remaining_display": time_display,
    "escalation_stage": escalation_stage,
    "escalation_pipeline": [
      {"tier": 1, "role": "Field Officer", "triggered": is_breached or is_near_breach},
      {"tier": 2, "role": "Ward Supervisor", "triggered": is_breached or is_near_breach},
      {"tier": 3, "role": "Department Head", "triggered": is_breached and hours_rem >= 48}
    ],
    "notified_roles": notified_roles
  }
