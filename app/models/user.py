"""
User model for authentication and user management
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, Boolean, DateTime, Enum, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    """User model"""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    company_name = Column(String)
    job_title = Column(String)
    phone = Column(String)
    plan = Column(Enum('starter', 'pro', 'enterprise', name='user_plan'), default='starter')
    role = Column(Enum('user', 'manager', 'admin', name='user_role'), default='user')
    preferences = Column(JSON, default={})
    integrations = Column(JSON, default={})
    email_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True, index=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'company_name': self.company_name,
            'job_title': self.job_title,
            'phone': self.phone,
            'plan': self.plan,
            'role': self.role,
            'preferences': self.preferences,
            'integrations': self.integrations,
            'email_verified': self.email_verified,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
