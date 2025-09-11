"""
Integration API routes
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_integrations():
    """List available integrations"""
    return {
        "integrations": [
            {"id": "salesforce", "name": "Salesforce", "status": "available"},
            {"id": "hubspot", "name": "HubSpot", "status": "available"},
            {"id": "zoom", "name": "Zoom", "status": "available"}
        ]
    }
