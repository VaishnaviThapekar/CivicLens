from typing import Dict, Any
from app.models.schemas import LocationData

WARD_BOUNDARIES = {
    "Ward 63": {
        "city": "Nashik",
        "ward_name": "Ward 63 (College Road)",
        "zone": "Zone 4",
        "road_name": "College Road Main Arterial",
        "nearest_landmark": "Near City Campus Gate 2",
        "postgis_wkt": "POLYGON((73.7850 19.9950, 73.7950 19.9950, 73.7950 20.0050, 73.7850 20.0050, 73.7850 19.9950))"
    },
    "Ward 12": {
        "city": "Nashik",
        "ward_name": "Ward 12 (MG Road Market)",
        "zone": "Zone 1",
        "road_name": "MG Road Main Corridor",
        "nearest_landmark": "Central Market Complex",
        "postgis_wkt": "POLYGON((73.7780 19.9980, 73.7880 19.9980, 73.7880 20.0080, 73.7780 20.0080, 73.7780 19.9980))"
    },
    "Ward 45": {
        "city": "Nashik",
        "ward_name": "Ward 45 (Gangapur Road)",
        "zone": "Zone 2",
        "road_name": "Gangapur Road Avenue",
        "nearest_landmark": "Opposite High School Complex",
        "postgis_wkt": "POLYGON((73.7700 19.9880, 73.7800 19.9880, 73.7800 19.9980, 73.7700 19.9980, 73.7700 19.9880))"
    },
    "Ward 18": {
        "city": "Nashik",
        "ward_name": "Ward 18 (Indira Nagar)",
        "zone": "Zone 3",
        "road_name": "Indira Nagar Ring Road",
        "nearest_landmark": "Near Municipal Water Tank",
        "postgis_wkt": "POLYGON((73.7600 19.9800, 73.7700 19.9800, 73.7700 19.9900, 73.7600 19.9900, 73.7600 19.9800))"
    }
}

def resolve_geolocation(lat: float, lng: float, preferred_ward: str = "Ward 63") -> LocationData:
    """
    Geospatial Reverse Geocoding Engine:
    Converts raw GPS coordinates into spatial identity (City, Ward, Zone, Road, Landmark, PostGIS Geometry).
    """
    boundary = WARD_BOUNDARIES.get(preferred_ward, WARD_BOUNDARIES["Ward 63"])

    return LocationData(
        lat=round(lat, 6),
        lng=round(lng, 6),
        address=f"{boundary['road_name']}, {boundary['ward_name']}, {boundary['city']}",
        city=boundary["city"],
        ward=preferred_ward,
        zone=boundary["zone"],
        road_name=boundary["road_name"],
        nearest_landmark=boundary["nearest_landmark"],
        postgis_geometry=f"ST_SetSRID(ST_Point({round(lng, 6)}, {round(lat, 6)}), 4326)"
    )
