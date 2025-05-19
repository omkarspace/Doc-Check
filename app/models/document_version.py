from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime
from typing import Dict, Any, Optional

class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=True)
    file_path = Column(String(512), nullable=False)
    changes = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    document = relationship("Document", back_populates="versions")
    creator = relationship("User", back_populates="document_versions")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the document version to a dictionary."""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "version_number": self.version_number,
            "content": self.content,
            "file_path": self.file_path,
            "changes": self.changes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by
        }

    def __repr__(self):
        return f"<DocumentVersion {self.document_id} v{self.version_number}>"
