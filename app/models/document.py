from uuid import uuid4
from enum import Enum
from sqlalchemy import Column, String, DateTime, JSON, Text, Enum as SQLEnum, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
from typing import Dict, Any, Optional, List

class DocumentType(str, Enum):
    LOAN_APPLICATION = "loan_application"
    CONTRACT = "contract"
    INVOICE = "invoice"
    KYC = "kyc"
    OTHER = "other"

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    file_path = Column(String(512), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="documents")
    versions = relationship("DocumentVersion", back_populates="document")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the document to a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "document_type": self.document_type,
            "file_path": self.file_path,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """Create a document from a dictionary."""
        return cls(
            id=data.get('id'),
            title=data['title'],
            content=data.get('content'),
            document_type=data.get('document_type', DocumentType.OTHER),
            file_path=data['file_path'],
            owner_id=data['owner_id']
        )
