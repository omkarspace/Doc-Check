from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Optional
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.models.user import User
from app.services.export_service import ExportService
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

@router.get("/document/{document_id}", tags=["export"])
async def export_document(
    document_id: int,
    format: str,
    version: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Export a single document
    """
    export_service = ExportService()
    return await export_service.export_document(
        document_id=document_id,
        format=format,
        version=version,
        db=db
    )

@router.get("/batch/{batch_id}", tags=["export"])
async def export_batch(
    batch_id: int,
    format: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Export all documents in a batch
    """
    export_service = ExportService()
    return await export_service.export_batch(
        batch_id=batch_id,
        format=format,
        db=db
    )

@router.get("/search", tags=["export"])
async def export_search_results(
    query: str,
    format: str,
    document_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Export search results
    """
    # Implement search functionality
    pass

@router.get("/custom", tags=["export"])
async def export_custom_fields(
    document_ids: List[int],
    fields: List[str],
    format: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Export custom fields for selected documents
    """
    # Implement custom field export
    pass
