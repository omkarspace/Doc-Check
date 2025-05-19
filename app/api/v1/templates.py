from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.template import Template
from app.models.schemas import TemplateInDB, TemplateInResponse, TemplateCreate
from app.security.auth import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=TemplateInResponse, status_code=status.HTTP_201_CREATED, tags=["templates"])
async def create_template(
    template: TemplateCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new document template
    """
    # Check if template with the same name already exists for this user
    existing_template = db.query(Template).filter(
        Template.name == template.name,
        Template.owner_id == current_user.id
    ).first()
    
    if existing_template:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A template with this name already exists"
        )
    
    # Create new template
    db_template = Template(
        name=template.name,
        description=template.description,
        fields=template.fields,
        owner_id=current_user.id
    )
    
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    return db_template

@router.get("/{template_id}", response_model=TemplateInResponse, tags=["templates"])
async def get_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a template by ID
    """
    template = db.query(Template).filter(Template.id == template_id).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Check if the user has permission to view this template
    if template.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this template"
        )
    
    return template

@router.get("/", response_model=List[TemplateInResponse], tags=["templates"])
async def list_templates(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all templates for the current user
    """
    if current_user.is_superuser:
        # Admin can see all templates
        templates = db.query(Template).offset(skip).limit(limit).all()
    else:
        # Regular users can only see their own templates
        templates = db.query(Template).filter(
            Template.owner_id == current_user.id
        ).offset(skip).limit(limit).all()
    
    return templates

@router.put("/{template_id}", response_model=TemplateInResponse, tags=["templates"])
async def update_template(
    template_id: int,
    template: TemplateCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a template
    """
    db_template = db.query(Template).filter(Template.id == template_id).first()
    
    if not db_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Check if the user has permission to update this template
    if db_template.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this template"
        )
    
    # Update template fields
    db_template.name = template.name
    db_template.description = template.description
    db_template.fields = template.fields
    
    db.commit()
    db.refresh(db_template)
    
    return db_template

@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["templates"])
async def delete_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a template
    """
    db_template = db.query(Template).filter(Template.id == template_id).first()
    
    if not db_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Check if the user has permission to delete this template
    if db_template.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this template"
        )
    
    db.delete(db_template)
    db.commit()
    
    return None
