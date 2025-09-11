"""
Call shadow model for manager coaching features
"""

import uuid
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Text, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class CallShadow(Base):
    """Call shadow model for real-time coaching"""
    
    __tablename__ = "call_shadows"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey('conversations.id'), nullable=False, index=True)
    manager_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    rep_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    coaching_notes = Column(JSON, default=[])  # Real-time coaching comments
    flagged_moments = Column(JSON, default=[])  # Important moments flagged by AI
    performance_tags = Column(JSON, default=[])  # Performance indicators
    improvement_areas = Column(JSON, default=[])  # Areas for improvement
    overall_score = Column(Float)
    detailed_scores = Column(JSON, default={})  # Breakdown by category
    summary = Column(Text)
    action_items = Column(Text)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
