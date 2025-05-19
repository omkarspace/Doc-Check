from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from enum import Enum

class DocumentType(str, Enum):
    LOAN_APPLICATION = "loan_application"
    CONTRACT = "contract"
    INVOICE = "invoice"
    KYC = "kyc"
    OTHER = "other"

# Request Models
class DocumentBase(BaseModel):
    title: str = Field(..., max_length=255)
    content: Optional[str] = None
    document_type: DocumentType
    metadata: Optional[Dict[str, Any]] = {}

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    document_type: Optional[DocumentType] = None
    metadata: Optional[Dict[str, Any]] = None

# Response Models
class DocumentInDBBase(DocumentBase):
    id: UUID
    status: str
    created_by: UUID
    updated_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Document(DocumentInDBBase):
    pass

class DocumentInDB(DocumentInDBBase):
    pass

# Response Wrappers
class DocumentResponse(BaseModel):
    success: bool
    data: Optional[Document] = None
    message: Optional[str] = None
    error: Optional[str] = None

class DocumentListResponse(BaseModel):
    success: bool
    data: List[Document]
    total: int
    message: Optional[str] = None
