"""
Analytics API routes
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/conversations/{conversation_id}")
async def get_conversation_analytics(conversation_id: str):
    """Get analytics for a specific conversation"""
    return {
        "conversation_id": conversation_id,
        "sentiment_score": 0.7,
        "engagement_score": 0.8,
        "objections_count": 2,
        "suggestions_used": 5
    }
