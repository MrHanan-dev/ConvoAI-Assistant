"""
User API routes
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/me")
async def get_current_user():
    """Get current user"""
    return {"id": "1", "email": "user@example.com", "name": "Test User"}
