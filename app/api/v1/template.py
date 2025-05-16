from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from app.models.template import Template, TemplateType
from app.services.template_service import TemplateService
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

@router.post("/create", tags=["templates"])
async def create_template(
    template_data: Dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new document template
    """
    template_service = TemplateService()
    return await template_service.create_template(
        template_data=template_data,
        owner_id=current_user.id,
        db=db
    )

@router.put("/{template_id}", tags=["templates"])
async def update_template(
    template_id: int,
    template_data: Dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing template
    """
    template_service = TemplateService()
    return await template_service.update_template(
        template_id=template_id,
        template_data=template_data,
        db=db
    )

@router.get("/{template_id}", tags=["templates"])
async def get_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific template by ID
    """
    template_service = TemplateService()
    return await template_service.get_template(
        template_id=template_id,
        db=db
    )

@router.get("/list", tags=["templates"])
async def list_templates(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all templates for the current user
    """
    template_service = TemplateService()
    return await template_service.list_templates(
        owner_id=current_user.id,
        db=db
    )

@router.delete("/{template_id}", tags=["templates"])
async def delete_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a template
    """
    template_service = TemplateService()
    await template_service.delete_template(
        template_id=template_id,
        db=db
    )
    return {"message": "Template deleted successfully"}

@router.post("/{template_id}/process", tags=["templates"])
async def process_document_with_template(
    template_id: int,
    document_text: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Process a document using a specific template
    """
    template_service = TemplateService()
    return await template_service.process_document_with_template(
        document_text=document_text,
        template_id=template_id,
        db=db
    )
