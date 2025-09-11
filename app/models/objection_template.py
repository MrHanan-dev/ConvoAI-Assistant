"""
Objection template model
"""

import uuid
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Text, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class ObjectionTemplate(Base):
    """Objection template model"""
    
    __tablename__ = "objection_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    team_id = Column(UUID(as_uuid=True), ForeignKey('teams.id'), nullable=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String, index=True)  # price, competition, timing, authority, etc.
    trigger_phrases = Column(JSON, default=[])  # Keywords that trigger this objection
    objection_text = Column(Text)
    response_template = Column(Text)
    alternative_responses = Column(JSON, default=[])
    battlecard_data = Column(JSON, default={})  # Competitive information
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
