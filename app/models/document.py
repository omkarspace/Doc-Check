from uuid import uuid4
from enum import Enum
from sqlalchemy import Column, String, DateTime, JSON, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database.database import Base
from typing import Dict, Any, Optional

class DocumentType(str, Enum):
    LOAN_APPLICATION = "loan_application"
    CONTRACT = "contract"
    INVOICE = "invoice"
    KYC = "kyc"
    OTHER = "other"

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid4()))
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    metadata = Column(JSON, default={}, nullable=True)
    status = Column(String(50), default="draft")
    created_by = Column(String(36), nullable=False)  # User ID
    updated_by = Column(String(36), nullable=True)   # User ID
    deleted_by = Column(String(36), nullable=True)   # User ID for soft delete
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)     # For soft delete

    def to_dict(self) -> Dict[str, Any]:
        """Convert the document to a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "document_type": self.document_type,
            "status": self.status,
            "metadata": self.metadata or {},
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """Create a document from a dictionary."""
        return cls(
            id=data.get('id'),
            title=data['title'],
            content=data.get('content', ''),
            document_type=data['document_type'],
            metadata=data.get('metadata', {}),
            status=data.get('status', 'draft'),
            created_by=data.get('created_by'),
            updated_by=data.get('updated_by')
        )
