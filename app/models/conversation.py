"""
Conversation and related models
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, String, Boolean, DateTime, Enum, JSON, Text, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Conversation(Base):
    """Conversation model"""
    
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    team_id = Column(UUID(as_uuid=True), ForeignKey('teams.id'), nullable=True, index=True)
    title = Column(String)
    type = Column(Enum('sales_call', 'interview', 'meeting', 'support', 'other', name='conversation_type'), default='meeting')
    platform = Column(Enum('zoom', 'teams', 'google_meet', 'other', name='conversation_platform'), default='other')
    started_at = Column(DateTime, index=True)
    ended_at = Column(DateTime)
    duration_seconds = Column(Integer)
    participants = Column(JSON, default=[])
    transcript = Column(Text)
    ai_suggestions = Column(JSON, default=[])
    objections_handled = Column(JSON, default=[])
    analytics = Column(JSON, default={})
    metadata = Column(JSON, default={})
    sentiment_score = Column(Float)
    engagement_score = Column(Float)
    clarity_score = Column(Float)
    conviction_score = Column(Float)
    outcome = Column(Enum('won', 'lost', 'follow_up', 'pending', name='conversation_outcome'), default='pending')
    summary = Column(Text)
    action_items = Column(Text)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'team_id': str(self.team_id) if self.team_id else None,
            'title': self.title,
            'type': self.type,
            'platform': self.platform,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'duration_seconds': self.duration_seconds,
            'participants': self.participants,
            'transcript': self.transcript,
            'ai_suggestions': self.ai_suggestions,
            'objections_handled': self.objections_handled,
            'analytics': self.analytics,
            'metadata': self.metadata,
            'sentiment_score': self.sentiment_score,
            'engagement_score': self.engagement_score,
            'clarity_score': self.clarity_score,
            'conviction_score': self.conviction_score,
            'outcome': self.outcome,
            'summary': self.summary,
            'action_items': self.action_items,
            'is_processed': self.is_processed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ObjectionEvent(Base):
    """Objection event model for tracking objections during conversations"""
    
    __tablename__ = "objection_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey('conversations.id'), nullable=False, index=True)
    objection_type = Column(String, nullable=False)
    objection_text = Column(Text, nullable=False)
    response_used = Column(Text)
    confidence_score = Column(Float)
    timestamp = Column(DateTime, nullable=False)
    speaker = Column(String, nullable=False)
    was_handled = Column(Boolean, default=False)
    handling_quality = Column(Float)  # 0-1 score for how well it was handled
    created_at = Column(DateTime, default=func.now())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'conversation_id': str(self.conversation_id),
            'objection_type': self.objection_type,
            'objection_text': self.objection_text,
            'response_used': self.response_used,
            'confidence_score': self.confidence_score,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'speaker': self.speaker,
            'was_handled': self.was_handled,
            'handling_quality': self.handling_quality,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
