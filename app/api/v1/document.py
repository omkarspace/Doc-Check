from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import List
from app.models.document import Document, DocumentType
from app.services.document_service import DocumentService
from app.security.auth import get_current_active_user
from app.database.database import SessionLocal
from sqlalchemy.orm import Session
import json

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload", tags=["documents"])
async def upload_document(
    file: UploadFile = File(...),
    document_type: DocumentType = DocumentType.OTHER,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload and process a document
    """
    if not file.filename.lower().endswith(tuple(settings.SUPPORTED_FILE_TYPES)):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported types: {settings.SUPPORTED_FILE_TYPES}"
        )

    # Read file content
    file_content = await file.read()
    
    # Process document
    document_service = DocumentService()
    try:
        processing_result = await document_service.process_document(
            file_content,
            file.filename.lower().split('.')[-1]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )

    # Save to database
    new_document = Document(
        filename=file.filename,
        file_type=file.filename.split('.')[-1],
        document_type=document_type,
        processed_text=processing_result["text"],
        ai_analysis=processing_result["analysis"],
        owner_id=current_user.id
    )
    
    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    return {
        "id": new_document.id,
        "filename": new_document.filename,
        "document_type": new_document.document_type,
        "status": "processed",
        "processed_text": processing_result["text"],
        "ai_analysis": processing_result["analysis"]
    }

@router.get("/list", tags=["documents"])
async def list_documents(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all documents for the current user
    """
    documents = db.query(Document).filter(Document.owner_id == current_user.id).all()
    return [doc.__dict__ for doc in documents]

@router.get("/{document_id}", tags=["documents"])
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific document by ID
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )
    
    return document.__dict__
