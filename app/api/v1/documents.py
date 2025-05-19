from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.document import Document, DocumentType
from app.models.schemas import DocumentCreate, DocumentInDB, DocumentInResponse
from app.security.auth import get_current_active_user
from app.models.user import User
from datetime import datetime
import uuid
import os

router = APIRouter()

@router.post("/", response_model=DocumentInResponse, status_code=status.HTTP_201_CREATED, tags=["documents"])
async def create_document(
    title: str = Form(...),
    document_type: DocumentType = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload a new document
    """
    # Generate a unique filename
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_extension}"
    
    # Save the file to the uploads directory
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, filename)
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Create document in database
    db_document = Document(
        title=title,
        document_type=document_type,
        file_path=file_path,
        owner_id=current_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return db_document

@router.get("/", response_model=List[DocumentInResponse], tags=["documents"])
async def read_documents(
    skip: int = 0,
    limit: int = 100,
    document_type: Optional[DocumentType] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve documents with optional filtering by type
    """
    query = db.query(Document)
    
    if document_type:
        query = query.filter(Document.document_type == document_type)
    
    # Regular users can only see their own documents
    if current_user.role != "admin":
        query = query.filter(Document.owner_id == current_user.id)
    
    documents = query.offset(skip).limit(limit).all()
    return documents

@router.get("/{document_id}", response_model=DocumentInResponse, tags=["documents"])
async def read_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific document by ID
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if user has permission to view this document
    if current_user.role != "admin" and document.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this document"
        )
    
    return document

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["documents"])
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a document
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if user has permission to delete this document
    if current_user.role != "admin" and document.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this document"
        )
    
    # Delete the file if it exists
    if document.file_path and os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    db.delete(document)
    db.commit()
    
    return None
