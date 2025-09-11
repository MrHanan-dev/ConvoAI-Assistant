"""
Audit log model for compliance and security
"""

import uuid
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class AuditLog(Base):
    """Audit log model"""
    
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True, index=True)
    action = Column(String, nullable=False, index=True)  # login, logout, create_conversation, etc.
    resource_type = Column(String, index=True)  # user, conversation, document, etc.
    resource_id = Column(UUID(as_uuid=True))
    details = Column(JSON, default={})  # Additional context
    ip_address = Column(String)
    user_agent = Column(String)
    created_at = Column(DateTime, default=func.now(), index=True)
