from typing import Dict, Any

def convert_openapi_to_postman(openapi_spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts OpenAPI 3.0 specification dictionary into Postman Collection v2.1 format.
    """
    postman_items = []
    paths = openapi_spec.get("paths", {})

    for path, methods in paths.items():
        for method, details in methods.items():
            if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                continue

            summary = details.get("summary") or f"{method.upper()} {path}"
            description = details.get("description", "")
            tags = details.get("tags", ["General"])
            tag_name = tags[0] if tags else "General"

            # Parse path segments for Postman url object
            clean_path = path.strip("/")
            path_segments = clean_path.split("/") if clean_path else []

            # Request headers
            headers = [
                {"key": "Content-Type", "value": "application/json", "type": "text"},
                {"key": "Authorization", "value": "Bearer {{authToken}}", "type": "text"}
            ]

            request_item = {
                "name": summary,
                "request": {
                    "method": method.upper(),
                    "header": headers,
                    "url": {
                        "raw": "{{baseUrl}}" + path,
                        "host": ["{{baseUrl}}"],
                        "path": path_segments
                    },
                    "description": description
                },
                "response": []
            }

            # Add body for POST/PUT/PATCH
            if method.lower() in ["post", "put", "patch"]:
                request_item["request"]["body"] = {
                    "mode": "raw",
                    "raw": "{\n  \"example\": \"data\"\n}",
                    "options": {
                        "raw": {
                            "language": "json"
                        }
                    }
                }

            # Group under tag folder if not exists
            folder = next((f for f in postman_items if f["name"] == tag_name), None)
            if not folder:
                folder = {"name": tag_name, "item": []}
                postman_items.append(folder)

            folder["item"].append(request_item)

    return {
        "info": {
            "_postman_id": "civiclens-api-collection-v21",
            "name": openapi_spec.get("info", {}).get("title", "CivicLens API Collection"),
            "description": openapi_spec.get("info", {}).get("description", "CivicLens API Postman Collection"),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": postman_items,
        "variable": [
            {
                "key": "baseUrl",
                "value": "http://localhost:8000",
                "type": "string"
            },
            {
                "key": "authToken",
                "value": "YOUR_JWT_TOKEN_HERE",
                "type": "string"
            }
        ]
    }
