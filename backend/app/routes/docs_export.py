from fastapi import APIRouter, Request
from app.services.openapi_export import convert_openapi_to_postman

router = APIRouter(prefix="/api/docs", tags=["Documentation & Exports"])

@router.get("/openapi.json")
def get_openapi_spec(request: Request):
    """Returns the full OpenAPI 3.0 specification for CivicLens API."""
    return request.app.openapi()

@router.get("/postman-collection.json")
def get_postman_collection(request: Request):
    """Generates and downloads Postman Collection v2.1 export for API testing."""
    spec = request.app.openapi()
    return convert_openapi_to_postman(spec)
