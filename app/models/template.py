from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime
from enum import Enum

class TemplateType(str, Enum):
    LOAN_APPLICATION = "loan_application"
    CONTRACT = "contract"
    INVOICE = "invoice"
    KYC = "kyc"
    CUSTOM = "custom"

class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    template_type = Column(Enum(TemplateType), nullable=False)
    fields = Column(JSON, nullable=False)  # JSON schema for template fields
    sample_data = Column(JSON)  # Example data structure
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="templates")

    def __repr__(self):
        return f"<Template {self.name} ({self.template_type})>"
