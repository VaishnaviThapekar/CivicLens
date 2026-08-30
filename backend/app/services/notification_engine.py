"""
CivicLens Notification Engine & Multi-Channel Dispatch Service (In-App & Email)
Triggers automated notifications for Citizens (Report Received, AI Analyzed, Assigned, Work Started, Resolved, Verification Requested, Reopened, Closed)
and Authorities (New Critical Issue, SLA Approaching, SLA Breached, Hotspot Detected, Verification Failed).
"""

from datetime import datetime
from typing import List, Dict, Any

NOTIFICATION_STORE: Dict[str, List[Dict[str, Any]]] = {
  "citizen@civiclens.org": [
    {
      "id": "n-101",
      "title": "Report Received",
      "message": "Your report CL-NK-2026-001284 has been successfully logged.",
      "event_type": "REPORT_RECEIVED",
      "channel": "IN_APP_AND_EMAIL",
      "read": False,
      "timestamp": datetime.now().isoformat()
    },
    {
      "id": "n-102",
      "title": "AI Verification Requested",
      "message": "PWD has marked CL-NK-2026-001284 resolved. Please verify the fix.",
      "event_type": "VERIFICATION_REQUESTED",
      "channel": "IN_APP_AND_EMAIL",
      "read": False,
      "timestamp": datetime.now().isoformat()
    }
  ],
  "authority_command": [
    {
      "id": "na-101",
      "title": "🚨 New Critical P1 Issue",
      "message": "Deep pothole crater detected on College Road (Ward 63). SLA: 4 Hours.",
      "event_type": "NEW_CRITICAL_ISSUE",
      "channel": "IN_APP_AND_EMAIL",
      "read": False,
      "timestamp": datetime.now().isoformat()
    },
    {
      "id": "na-102",
      "title": "⚠️ SLA Breached",
      "message": "Ticket CL-NK-2026-001201 reached Tier 2 Supervisor Escalation.",
      "event_type": "SLA_BREACHED",
      "channel": "IN_APP_AND_EMAIL",
      "read": False,
      "timestamp": datetime.now().isoformat()
    }
  ]
}

def send_notification(
  recipient_key: str,
  title: str,
  message: str,
  event_type: str,
  channel: str = "IN_APP_AND_EMAIL"
) -> dict:
  """
  Dispatches notification to in-app store and simulates email template delivery.
  """
  if recipient_key not in NOTIFICATION_STORE:
    NOTIFICATION_STORE[recipient_key] = []

  notif = {
    "id": f"n-{len(NOTIFICATION_STORE[recipient_key]) + 101}",
    "title": title,
    "message": message,
    "event_type": event_type,
    "channel": channel,
    "email_sent": True,
    "email_template": "CIVICLENS_STANDARD_NOTIF_V1",
    "read": False,
    "timestamp": datetime.now().isoformat()
  }

  NOTIFICATION_STORE[recipient_key].append(notif)
  return notif

def get_user_notifications(recipient_key: str) -> List[Dict[str, Any]]:
  return NOTIFICATION_STORE.get(recipient_key, [])
