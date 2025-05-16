from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.database import Base
from datetime import datetime

class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    processed_text = Column(JSON)
    ai_analysis = Column(JSON)
    changes = Column(JSON)  # Changes made in this version
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))

    document = relationship("Document", back_populates="versions")
    creator = relationship("User")

    def __repr__(self):
        return f"<DocumentVersion {self.document_id} v{self.version_number}>"
