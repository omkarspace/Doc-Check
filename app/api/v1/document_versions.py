from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.document import Document
from app.models.document_version import DocumentVersion
# Import the DocumentVersion schemas
from app.models.schemas import DocumentVersionInResponse
from app.security.auth import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/{document_id}/versions", response_model=List[DocumentVersionInResponse], tags=["document_versions"])
async def get_document_versions(
    document_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all versions of a document
    """
    # Check if the document exists and the user has access to it
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if document.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this document"
        )
    
    # Get document versions
    versions = db.query(DocumentVersion)\
        .filter(DocumentVersion.document_id == document_id)\
        .order_by(DocumentVersion.version_number.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return versions

@router.get("/{document_id}/versions/{version_number}", response_model=DocumentVersionInResponse, tags=["document_versions"])
async def get_document_version(
    document_id: int,
    version_number: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific version of a document
    """
    # Check if the document exists and the user has access to it
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if document.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this document"
        )
    
    # Get the specific version
    version = db.query(DocumentVersion)\
        .filter(
            DocumentVersion.document_id == document_id,
            DocumentVersion.version_number == version_number
        )\
        .first()
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_number} not found for document {document_id}"
        )
    
    return version
