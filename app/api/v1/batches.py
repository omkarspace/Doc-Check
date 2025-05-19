from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from typing import List, Optional
import shutil
import os
from sqlalchemy.orm import Session
from datetime import datetime

from app.database.database import get_db
from app.models.batch import Batch, BatchStatus
from app.models.document import Document, DocumentType
from app.models.user import User
from app.models.schemas import BatchInDB, BatchInResponse, BatchCreate
from app.security.auth import get_current_active_user
from app.services.batch_processor import process_batch

router = APIRouter()

UPLOAD_DIR = "uploads/batches"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=BatchInResponse, status_code=status.HTTP_201_CREATED, tags=["batches"])
async def create_batch(
    background_tasks: BackgroundTasks,
    name: str,
    description: Optional[str] = None,
    document_type: DocumentType = DocumentType.OTHER,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new batch of documents for processing
    """
    # Create batch directory
    batch_dir = os.path.join(UPLOAD_DIR, f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{name}")
    os.makedirs(batch_dir, exist_ok=True)
    
    # Save files to batch directory
    file_paths = []
    for file in files:
        file_path = os.path.join(batch_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_paths.append(file_path)
    
    # Create batch record
    db_batch = Batch(
        name=name,
        description=description,
        document_type=document_type,
        file_path=batch_dir,
        status=BatchStatus.PENDING,
        owner_id=current_user.id,
        document_count=len(files)
    )
    
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    
    # Process batch in background
    background_tasks.add_task(process_batch, db_batch.id, db)
    
    return db_batch

@router.get("/{batch_id}", response_model=BatchInResponse, tags=["batches"])
async def get_batch(
    batch_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get batch by ID
    """
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    # Check permissions
    if batch.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this batch"
        )
    
    return batch

@router.get("/", response_model=List[BatchInResponse], tags=["batches"])
async def list_batches(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all batches for the current user
    """
    if current_user.is_superuser:
        # Admin can see all batches
        batches = db.query(Batch).offset(skip).limit(limit).all()
    else:
        # Regular users can only see their own batches
        batches = db.query(Batch).filter(
            Batch.owner_id == current_user.id
        ).offset(skip).limit(limit).all()
    
    return batches

@router.delete("/{batch_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["batches"])
async def delete_batch(
    batch_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a batch and its associated files
    """
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    # Check permissions
    if batch.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this batch"
        )
    
    # Delete files
    if os.path.exists(batch.file_path):
        shutil.rmtree(batch.file_path)
    
    # Delete batch record
    db.delete(batch)
    db.commit()
    
    return None
