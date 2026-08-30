"""
CivicLens Smart Infrastructure IoT Sensor Stream & Drone Audit Engine
Simulates real-time telemetry from Smart Trash Bins (fill level > 85%), Manhole Cover Pressure Sensors, Streetlight Outage Detectors, and Drone Inspection Feeds.
"""

from typing import List, Dict, Any
from datetime import datetime

def get_live_iot_sensor_feed() -> List[Dict[str, Any]]:
    return [
        {
            "sensor_id": "IOT-BIN-6301",
            "sensor_name": "Smart Waste Bin #6301",
            "type": "TRASH_BIN_FILL_LEVEL",
            "location": "College Road Bus Stop (Ward 63)",
            "telemetry_value": "89% Fill Level",
            "status": "CRITICAL_THRESHOLD_EXCEEDED",
            "auto_ticket_created": "CL-NK-2026-001288",
            "last_updated": datetime.now().isoformat()
        },
        {
            "sensor_id": "IOT-MANHOLE-4202",
            "sensor_name": "Sub-Surface Manhole Pressure Sensor",
            "type": "MANHOLE_PRESSURE",
            "location": "Market Street Link (Ward 42)",
            "telemetry_value": "Pressure Drop 18 PSI",
            "status": "UNDERGROUND_LEAK_ALERT",
            "auto_ticket_created": "CL-NK-2026-001289",
            "last_updated": datetime.now().isoformat()
        },
        {
            "sensor_id": "IOT-[#287C73]-LIGHT-1205",
            "sensor_name": "Smart Streetlight Grid Node #1205",
            "type": "STREETLIGHT_OUTAGE",
            "location": "Arterial Corridor (Ward 12)",
            "telemetry_value": "0 Lumen Current Flow",
            "status": "POWER_GRID_OUTAGE",
            "auto_ticket_created": "CL-NK-2026-001290",
            "last_updated": datetime.now().isoformat()
        }
    ]

def get_drone_inspection_audits() -> List[Dict[str, Any]]:
    return [
        {
            "drone_id": "DRONE-AERIAL-04",
            "zone": "Ward 63 Flash Inundation Zone",
            "altitude_m": 45,
            "area_scanned_m2": 12500,
            "waterlogging_extent_detected": "450 sq meters",
            "cv_confidence": "96% High Match",
            "timestamp": datetime.now().isoformat()
        }
    ]
