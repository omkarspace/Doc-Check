from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from app.models.document import DocumentType
from app.models.batch import BatchStatus

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: int
    hashed_password: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserInResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

# Document Schemas
class DocumentBase(BaseModel):
    title: str
    document_type: str
    file_path: str
    owner_id: int

class DocumentCreate(DocumentBase):
    pass

class DocumentInDB(DocumentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DocumentInResponse(DocumentInDB):
    class Config:
        from_attributes = True

# Document Version Schemas
class DocumentVersionBase(BaseModel):
    document_id: int
    version_number: int
    changes: Optional[dict] = None
    content: Optional[str] = None
    file_path: str
    created_by: int

class DocumentVersionCreate(DocumentVersionBase):
    pass

class DocumentVersionInDB(DocumentVersionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentVersionInResponse(DocumentVersionInDB):
    class Config:
        from_attributes = True

# Template Schemas
class TemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    fields: dict

class TemplateCreate(TemplateBase):
    pass

class TemplateInDB(TemplateBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TemplateInResponse(TemplateInDB):
    class Config:
        from_attributes = True

# Batch Schemas
class BatchBase(BaseModel):
    name: str
    description: Optional[str] = None
    document_type: DocumentType

class BatchCreate(BatchBase):
    pass

class BatchInDB(BatchBase):
    id: int
    file_path: str
    status: BatchStatus
    document_count: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BatchInResponse(BatchInDB):
    class Config:
        from_attributes = True
