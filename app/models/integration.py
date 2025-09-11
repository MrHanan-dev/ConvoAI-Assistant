"""
Integration model for CRM and third-party connections
"""

import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Enum, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class Integration(Base):
    """Integration model"""
    
    __tablename__ = "integrations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    team_id = Column(UUID(as_uuid=True), ForeignKey('teams.id'), nullable=True, index=True)
    provider = Column(Enum('salesforce', 'hubspot', 'zoom', 'teams', 'google_meet', 'slack', 'other', name='integration_provider'), nullable=False, index=True)
    external_id = Column(String)  # ID in external system
    credentials = Column(JSON)  # Encrypted credentials
    settings = Column(JSON, default={})
    sync_status = Column(JSON, default={})
    is_active = Column(Boolean, default=True, index=True)
    last_sync_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
