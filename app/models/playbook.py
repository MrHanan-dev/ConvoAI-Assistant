"""
Playbook model for sales methodology and talk tracks
"""

import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Enum, JSON, Text, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class Playbook(Base):
    """Playbook model"""
    
    __tablename__ = "playbooks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    team_id = Column(UUID(as_uuid=True), ForeignKey('teams.id'), nullable=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    type = Column(Enum('sales', 'support', 'interview', 'demo', 'other', name='playbook_type'), default='sales', index=True)
    talk_tracks = Column(JSON, default=[])  # Structured conversation flows
    message_frameworks = Column(JSON, default=[])  # Key messaging points
    question_sequences = Column(JSON, default=[])  # Discovery questions
    closing_techniques = Column(JSON, default=[])  # Closing strategies
    objection_handling = Column(JSON, default=[])  # Linked objection templates
    success_criteria = Column(JSON, default={})  # KPIs and goals
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
