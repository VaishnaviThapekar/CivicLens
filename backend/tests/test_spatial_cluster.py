from app.services.spatial_cluster import cluster_complaints
from app.models.schemas import Complaint, LocationData, PriorityLevel, ComplaintStatus, ComplaintCategory

def test_spatial_clustering():
    c1 = Complaint(
        id="c-1",
        tracking_number="CL-1",
        title="Pothole 1",
        description="Pothole on main road",
        category=ComplaintCategory.ROAD_INFRASTRUCTURE,
        priority=PriorityLevel.P1,
        priority_reason="Accident risk",
        status=ComplaintStatus.SUBMITTED,
        location=LocationData(lat=19.9975, lng=73.7898, address="College Road", city="Nashik", ward="Ward 63")
    )
    c2 = Complaint(
        id="c-2",
        tracking_number="CL-2",
        title="Pothole 2",
        description="Same pothole reported again",
        category=ComplaintCategory.ROAD_INFRASTRUCTURE,
        priority=PriorityLevel.P1,
        priority_reason="Accident risk",
        status=ComplaintStatus.SUBMITTED,
        location=LocationData(lat=19.9976, lng=73.7899, address="College Road", city="Nashik", ward="Ward 63")
    )

    clusters = cluster_complaints([c1, c2])
    assert len(clusters) == 1
    assert clusters[0].supporting_reports_count == 2
    assert "c-1" in clusters[0].report_ids
    assert "c-2" in clusters[0].report_ids

def test_faraway_no_cluster():
    c1 = Complaint(
        id="c-1",
        tracking_number="CL-1",
        title="Pothole 1",
        description="Pothole in Ward 63",
        category=ComplaintCategory.ROAD_INFRASTRUCTURE,
        priority=PriorityLevel.P1,
        priority_reason="Accident risk",
        status=ComplaintStatus.SUBMITTED,
        location=LocationData(lat=19.9975, lng=73.7898, address="College Road", city="Nashik", ward="Ward 63")
    )
    c3 = Complaint(
        id="c-3",
        tracking_number="CL-3",
        title="Streetlight Failure",
        description="Dark street in Ward 18",
        category=ComplaintCategory.STREETLIGHT_ELECTRICAL,
        priority=PriorityLevel.P3,
        priority_reason="Night visibility",
        status=ComplaintStatus.SUBMITTED,
        location=LocationData(lat=19.9850, lng=73.7680, address="Indira Nagar", city="Nashik", ward="Ward 18")
    )

    clusters = cluster_complaints([c1, c3])
    assert len(clusters) == 0
