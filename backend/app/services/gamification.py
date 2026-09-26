"""
CivicLens Gamified Citizen Impact & Rewards Engine
Calculates Civic Karma Points, Badges, Ward Leaderboards, and Municipal Tax Rebate Vouchers.
"""

from typing import List, Dict, Any

def get_citizen_impact_stats(email: str = "citizen@civiclens.org") -> Dict[str, Any]:
    return {
        "user_email": email,
        "full_name": "Alex Morgan",
        "civic_karma_points": 4850,
        "impact_rank": "#3 in Ward 63",
        "level": "Level 5 — Master Urban Guardian",
        "badges": [
            {"title": "College Road Urban Guardian", "icon": "🛡️", "date": "Aug 2026", "desc": "Filed 20+ verified civic reports"},
            {"title": "Zero Waste Pioneer", "icon": "♻️", "date": "Jul 2026", "desc": "Flagged 15 illegal dumping sites"},
            {"title": "Resolution Verifier", "icon": "👁️", "date": "Jun 2026", "desc": "Verified 10 officer repair uploads"}
        ],
        "rewards": [
            {"title": "₹200 Municipal Parking Credit", "code": "CIVIC-PARK-2026", "status": "AVAILABLE"},
            {"title-[#287C73]": "5% Property Tax Rebate Voucher", "code": "CIVIC-TAX-5PCT", "status": "AVAILABLE"}
        ]
    }

def get_ward_leaderboard() -> List[Dict[str, Any]]:
    return [
        {"rank": 1, "name": "Rajesh Kumar", "ward": "Ward 63", "karma": 6200, "reports": 34, "badge": "👑 Champion"},
        {"rank": 2, "name": "Priya Sharma", "ward": "Ward 12", "karma": 5400, "reports": 29, "badge": "⭐ Star Guardian"},
        {"rank": 3, "name": "Alex Morgan", "ward": "Ward 63", "karma": 4850, "reports": 24, "badge": "🛡️ Master Guardian"},
        {"rank": 4, "name": "Amit Patil", "ward": "Ward 45", "karma": 4100, "reports": 19, "badge": "🏅 Civic Veteran"},
        {"rank": 5, "name": "Sneha Deshmukh", "ward": "Ward 18", "karma": 3750, "reports": 16, "badge": "🌱 Active Citizen"}
    ]

def calculate_karma_award(action_type: str, has_exif_telemetry: bool = False, is_ground_verified: bool = False) -> Dict[str, Any]:
    """
    Calculates dynamic karma point awards based on citizen contribution quality.
    - Base report submission: +50 pts
    - High-quality EXIF GPS photo telemetry bonus: +25 pts
    - Ground repair verification bonus: +30 pts
    - Participatory governance vote: +15 pts
    """
    base_points = 50
    if action_type == "VERIFY_REPAIR":
        base_points = 30
    elif action_type == "GOVERNANCE_VOTE":
        base_points = 15

    bonus = 0
    reasons = []
    if has_exif_telemetry:
        bonus += 25
        reasons.append("High-quality EXIF GPS telemetry verified (+25 pts)")
    if is_ground_verified:
        bonus += 30
        reasons.append("Ground repair verification completed (+30 pts)")

    total = base_points + bonus
    return {
        "action_type": action_type,
        "base_points": base_points,
        "bonus_points": bonus,
        "total_karma_awarded": total,
        "bonus_reasons": reasons
    }
