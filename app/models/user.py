from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
        
    def verify_password(self, password: str) -> bool:
        """Verify password against stored hash."""
        return pwd_context.verify(password, self.hashed_password)
        
    def set_password(self, password: str) -> None:
        """Set a new password."""
        self.hashed_password = pwd_context.hash(password)
        
    @classmethod
    def get_by_email(cls, db, email: str):
        """Get user by email."""
        return db.query(cls).filter(cls.email == email).first()
        
    def to_dict(self):
        """Convert user object to dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "role": self.role.value,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
