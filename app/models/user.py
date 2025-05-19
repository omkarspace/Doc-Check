from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional

class UserRole(str, PyEnum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    documents = relationship("Document", back_populates="owner")
    document_versions = relationship("DocumentVersion", back_populates="creator")
    templates = relationship("Template", back_populates="owner")
    batches = relationship("Batch", back_populates="owner")

    @property
    def is_superuser(self) -> bool:
        return self.role == UserRole.ADMIN
