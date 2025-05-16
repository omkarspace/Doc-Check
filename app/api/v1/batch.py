from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List, Dict
from app.models.batch import Batch, BatchStatus
from app.services.batch_processor import BatchProcessor
from app.security.auth import get_current_active_user
from app.database.database import SessionLocal
from sqlalchemy.orm import Session
from datetime import datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create", tags=["batch"])
async def create_batch(
    name: str,
    description: str,
    document_type: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new batch processing job
    """
    batch_processor = BatchProcessor()
    return await batch_processor.create_batch(
        name=name,
        description=description,
        document_type=document_type,
        owner_id=current_user.id,
        db=db
    )

@router.post("/{batch_id}/add-documents", tags=["batch"])
async def add_documents_to_batch(
    batch_id: int,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add documents to an existing batch
    """
    batch_processor = BatchProcessor()
    return await batch_processor.add_documents_to_batch(
        batch_id=batch_id,
        files=files,
        db=db
    )

@router.post("/{batch_id}/process", tags=["batch"])
async def process_batch(
    batch_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Process all documents in a batch
    """
    batch_processor = BatchProcessor()
    return await batch_processor.process_batch(
        batch_id=batch_id,
        db=db
    )

@router.get("/{batch_id}/status", tags=["batch"])
async def get_batch_status(
    batch_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get the status of a batch processing job
    """
    batch_processor = BatchProcessor()
    return await batch_processor.get_batch_status(
        batch_id=batch_id,
        db=db
    )

@router.get("/list", tags=["batch"])
async def list_batches(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all batches for the current user
    """
    batch_processor = BatchProcessor()
    return await batch_processor.list_batches(
        owner_id=current_user.id,
        db=db
    )
