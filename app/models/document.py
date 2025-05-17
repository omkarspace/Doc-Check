from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime
from enum import Enum as PyEnum

class DocumentType(str, PyEnum):
    LOAN_APPLICATION = "loan_application"
    CONTRACT = "contract"
    INVOICE = "invoice"
    KYC = "kyc"
    OTHER = "other"

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    status = Column(String, default="processing")
    processed_text = Column(JSON)
    ai_analysis = Column(JSON)
    owner_id = Column(Integer, ForeignKey("users.id"))
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="documents")
    versions = relationship("DocumentVersion", back_populates="document")
    batch = relationship("Batch", back_populates="documents")
