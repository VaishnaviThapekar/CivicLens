"""
CivicLens Participatory Ward Budgeting & Townhall Voting Engine
Allows citizens to vote on municipal ward infrastructure proposals using earned Civic Karma points.
"""

from typing import List, Dict, Any

PROPOSALS_STORE = [
    {
        "id": "prop-101",
        "title": "Ward 63 Streetlight LED & Solar Grid Upgrade",
        "category": "Electrical & Public Safety",
        "estimated_budget_inr": "₹45,000,000",
        "votes_count": 342,
        "karma_points_allocated": 17100,
        "status": "VOTING_ACTIVE",
        "description": "Install 120 solar-powered LED streetlights along dark pedestrian corridors."
    },
    {
        "id": "prop-102",
        "title": "College Road Stormwater Drainage Culvert Resurfacing",
        "category": "Drainage & Flood Mitigation",
        "estimated_budget_inr": "₹82,000,000",
        "votes_count": 518,
        "karma_points_allocated": 25900,
        "status": "APPROVED_FOR_TENDER",
        "description": "Expand culvert capacity to prevent urban flash flooding during monsoon."
    },
    {
        "id": "prop-103",
        "title": "Ward 63 Zero-Waste Automated Composting Station",
        "category": "Sanitation & Environment",
        "estimated_budget_inr": "₹28,000,000",
        "votes_count": 289,
        "karma_points_allocated": 14450,
        "status": "VOTING_ACTIVE",
        "description": "Deploy decentralized organic waste processing unit for 2,500 households."
    }
]

def get_proposals() -> List[Dict[str, Any]]:
    return PROPOSALS_STORE

def vote_proposal(proposal_id: str, karma_pts: int = 50) -> Dict[str, Any]:
    for prop in PROPOSALS_STORE:
        if prop["id"] == proposal_id:
            prop["votes_count"] += 1
            prop["karma_points_allocated"] += karma_pts
            return {"status": "success", "message": f"Voted successfully! Allocated {karma_pts} Karma PTS to '{prop['title']}'", "updated_proposal": prop}
    return {"status": "error", "message": "Proposal not found"}
