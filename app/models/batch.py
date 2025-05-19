from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List, Dict, Any

class BatchStatus(str, PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Batch(Base):
    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(BatchStatus), default=BatchStatus.PENDING, nullable=False)
    document_type = Column(String(50), nullable=False)
    file_path = Column(String(512), nullable=False)  # Path to the batch directory
    document_count = Column(Integer, default=0, nullable=False)  # Total number of documents in the batch
    processed_count = Column(Integer, default=0, nullable=False)  # Number of successfully processed documents
    failed_count = Column(Integer, default=0, nullable=False)  # Number of failed documents
    metadata_ = Column("metadata", JSON, default=dict, nullable=True)  # Additional metadata
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    started_at = Column(DateTime, nullable=True)  # When processing started
    completed_at = Column(DateTime, nullable=True)  # When processing completed/failed
    
    # Relationships
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="batches")
    documents = relationship("Document", back_populates="batch", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Batch {self.id}: {self.name} ({self.status})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the batch to a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "document_type": self.document_type,
            "document_count": self.document_count,
            "processed_count": self.processed_count,
            "failed_count": self.failed_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "owner_id": self.owner_id
        }
