"""
Team and team member models
"""

import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Enum, JSON, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from typing import Dict, Any

from app.core.database import Base


class Team(Base):
    """Team model"""
    
    __tablename__ = "teams"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    settings = Column(JSON, default={})
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class TeamMember(Base):
    """Team member model"""
    
    __tablename__ = "team_members"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey('teams.id'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    role = Column(Enum('member', 'manager', 'admin', name='team_member_role'), default='member')
    permissions = Column(JSON, default={})
    joined_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
