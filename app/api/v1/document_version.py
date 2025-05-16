from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from app.models.document_version import DocumentVersion
from app.services.document_version_service import DocumentVersionService
from app.security.auth import get_current_active_user
from app.database.database import SessionLocal
from sqlalchemy.orm import Session

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/{document_id}/create", tags=["document_versions"])
async def create_version(
    document_id: int,
    processed_text: Dict,
    ai_analysis: Dict,
    changes: Dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new version of a document
    """
    version_service = DocumentVersionService()
    return await version_service.create_version(
        document_id=document_id,
        processed_text=processed_text,
        ai_analysis=ai_analysis,
        changes=changes,
        created_by=current_user.id,
        db=db
    )

@router.get("/{document_id}/{version_number}", tags=["document_versions"])
async def get_version(
    document_id: int,
    version_number: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific version of a document
    """
    version_service = DocumentVersionService()
    return await version_service.get_version(
        document_id=document_id,
        version_number=version_number,
        db=db
    )

@router.get("/{document_id}/list", tags=["document_versions"])
async def list_versions(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all versions of a document
    """
    version_service = DocumentVersionService()
    return await version_service.list_versions(
        document_id=document_id,
        db=db
    )

@router.get("/{document_id}/compare", tags=["document_versions"])
async def compare_versions(
    document_id: int,
    version1: int,
    version2: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Compare two versions of a document
    """
    version_service = DocumentVersionService()
    return await version_service.compare_versions(
        document_id=document_id,
        version1=version1,
        version2=version2,
        db=db
    )
