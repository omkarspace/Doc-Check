from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime

class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    fields = Column(JSON, nullable=False)  # JSON schema for template fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="templates")

    def __repr__(self):
        return f"<Template {self.name} (ID: {self.id})>"
    
    def to_dict(self):
        """Convert the template to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "fields": self.fields,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
