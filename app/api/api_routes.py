"""
API routes for the AI Conversation Assistant
"""

from fastapi import APIRouter

# Import all route modules from the routes subdirectory
from .routes import auth, conversations, analytics, integrations, documents, users

# Create main router
api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["Conversations"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["Integrations"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
