from typing import List, Dict, Optional
from app.models.document_version import DocumentVersion
from app.database.database import SessionLocal
from sqlalchemy.orm import Session
import json

class DocumentVersionService:
    def __init__(self):
        pass

    async def create_version(
        self,
        document_id: int,
        processed_text: Dict,
        ai_analysis: Dict,
        changes: Dict,
        created_by: int,
        db: Session
    ) -> Dict:
        """
        Create a new version of a document
        """
        # Get the latest version number
        latest_version = db.query(DocumentVersion).filter(
            DocumentVersion.document_id == document_id
        ).order_by(DocumentVersion.version_number.desc()).first()

        version_number = 1 if not latest_version else latest_version.version_number + 1

        version = DocumentVersion(
            document_id=document_id,
            version_number=version_number,
            processed_text=processed_text,
            ai_analysis=ai_analysis,
            changes=changes,
            created_by=created_by
        )

        db.add(version)
        db.commit()
        db.refresh(version)

        return version.__dict__

    async def get_version(
        self,
        document_id: int,
        version_number: int,
        db: Session
    ) -> Dict:
        """
        Get a specific version of a document
        """
        version = db.query(DocumentVersion).filter(
            DocumentVersion.document_id == document_id,
            DocumentVersion.version_number == version_number
        ).first()

        if not version:
            raise ValueError("Version not found")

        return version.__dict__

    async def list_versions(
        self,
        document_id: int,
        db: Session
    ) -> List[Dict]:
        """
        List all versions of a document
        """
        versions = db.query(DocumentVersion).filter(
            DocumentVersion.document_id == document_id
        ).order_by(DocumentVersion.version_number.asc()).all()

        return [version.__dict__ for version in versions]

    async def compare_versions(
        self,
        document_id: int,
        version1: int,
        version2: int,
        db: Session
    ) -> Dict:
        """
        Compare two versions of a document
        """
        v1 = db.query(DocumentVersion).filter(
            DocumentVersion.document_id == document_id,
            DocumentVersion.version_number == version1
        ).first()

        v2 = db.query(DocumentVersion).filter(
            DocumentVersion.document_id == document_id,
            DocumentVersion.version_number == version2
        ).first()

        if not v1 or not v2:
            raise ValueError("One or both versions not found")

        return {
            "version1": v1.version_number,
            "version2": v2.version_number,
            "text_changes": self._compare_text(v1.processed_text, v2.processed_text),
            "analysis_changes": self._compare_analysis(v1.ai_analysis, v2.ai_analysis)
        }

    def _compare_text(self, text1: Dict, text2: Dict) -> Dict:
        """
        Compare processed text between two versions
        """
        changes = {}
        for key in set(list(text1.keys()) + list(text2.keys())):
            if text1.get(key) != text2.get(key):
                changes[key] = {
                    "old": text1.get(key),
                    "new": text2.get(key)
                }
        return changes

    def _compare_analysis(self, analysis1: Dict, analysis2: Dict) -> Dict:
        """
        Compare AI analysis between two versions
        """
        changes = {}
        for key in set(list(analysis1.keys()) + list(analysis2.keys())):
            if analysis1.get(key) != analysis2.get(key):
                changes[key] = {
                    "old": analysis1.get(key),
                    "new": analysis2.get(key)
                }
        return changes
