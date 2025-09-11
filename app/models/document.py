"""
Document model
"""

import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Enum, JSON, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from typing import Dict, Any

from app.core.database import Base


class Document(Base):
    """Document model"""
    
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    team_id = Column(UUID(as_uuid=True), ForeignKey('teams.id'), nullable=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    type = Column(Enum('sales_deck', 'product_sheet', 'whitepaper', 'faq', 'battlecard', 'other', name='document_type'), default='other')
    file_path = Column(String)
    file_url = Column(String)
    mime_type = Column(String)
    file_size = Column(Integer)
    content = Column(Text)  # Extracted text content
    embeddings = Column(JSON)  # Vector embeddings
    tags = Column(JSON, default=[])
    metadata = Column(JSON, default={})
    is_active = Column(Boolean, default=True, index=True)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'team_id': str(self.team_id) if self.team_id else None,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'file_path': self.file_path,
            'file_url': self.file_url,
            'mime_type': self.mime_type,
            'file_size': self.file_size,
            'tags': self.tags,
            'metadata': self.metadata,
            'is_active': self.is_active,
            'is_processed': self.is_processed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
