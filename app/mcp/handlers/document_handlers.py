from typing import Optional, Dict, Any, List
from uuid import UUID
from sqlalchemy.orm import Session

from ...database import SessionLocal
from ...models.document import Document as DocumentModel
from ...mcp import command_handler
from ...mcp.base import CommandResponse
from ..commands.document_commands import (
    CreateDocumentCommand,
    UpdateDocumentCommand,
    DeleteDocumentCommand
)
from ..queries.document_queries import (
    GetDocumentQuery,
    ListDocumentsQuery,
    SearchDocumentsQuery
)

# Command Handlers
@command_handler(CreateDocumentCommand)
async def handle_create_document(command: CreateDocumentCommand) -> CommandResponse[Dict[str, Any]]:
    """Handle document creation."""
    db = SessionLocal()
    try:
        # Create new document
        db_document = DocumentModel(
            title=command.title,
            content=command.content,
            document_type=command.document_type,
            metadata=command.metadata or {},
            created_by=str(command.created_by)
        )
        
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        return CommandResponse.success(
            data={"id": db_document.id},
            message="Document created successfully",
            status_code=201
        )
    except Exception as e:
        db.rollback()
        return CommandResponse.error(
            error=str(e),
            message="Failed to create document",
            status_code=400
        )
    finally:
        db.close()

@command_handler(UpdateDocumentCommand)
async def handle_update_document(command: UpdateDocumentCommand) -> CommandResponse[Dict[str, Any]]:
    """Handle document update."""
    db = SessionLocal()
    try:
        # Get existing document
        document = db.query(DocumentModel).filter(DocumentModel.id == str(command.document_id)).first()
        if not document:
            return CommandResponse.error(
                error="Document not found",
                status_code=404
            )
        
        # Update fields if provided
        if command.title is not None:
            document.title = command.title
        if command.content is not None:
            document.content = command.content
        if command.metadata is not None:
            document.metadata = command.metadata
        
        document.updated_by = str(command.updated_by)
        
        db.commit()
        db.refresh(document)
        
        return CommandResponse.success(
            data={"id": document.id},
            message="Document updated successfully"
        )
    except Exception as e:
        db.rollback()
        return CommandResponse.error(
            error=str(e),
            message="Failed to update document",
            status_code=400
        )
    finally:
        db.close()

@command_handler(DeleteDocumentCommand)
async def handle_delete_document(command: DeleteDocumentCommand) -> CommandResponse[None]:
    """Handle document deletion."""
    db = SessionLocal()
    try:
        document = db.query(DocumentModel).filter(DocumentModel.id == str(command.document_id)).first()
        if not document:
            return CommandResponse.error(
                error="Document not found",
                status_code=404
            )
        
        # Soft delete by updating deleted_by
        document.deleted_by = str(command.deleted_by)
        db.commit()
        
        return CommandResponse.success(
            message="Document deleted successfully"
        )
    except Exception as e:
        db.rollback()
        return CommandResponse.error(
            error=str(e),
            message="Failed to delete document",
            status_code=400
        )
    finally:
        db.close()

# Query Handlers
@command_handler(GetDocumentQuery)
async def handle_get_document(query: GetDocumentQuery) -> CommandResponse[Dict[str, Any]]:
    """Handle document retrieval by ID."""
    db = SessionLocal()
    try:
        document = db.query(DocumentModel).filter(
            DocumentModel.id == str(query.document_id),
            DocumentModel.deleted_by.is_(None)  # Only non-deleted documents
        ).first()
        
        if not document:
            return CommandResponse.error(
                error="Document not found",
                status_code=404
            )
            
        return CommandResponse.success(
            data=document.to_dict(),
            message="Document retrieved successfully"
        )
    except Exception as e:
        return CommandResponse.error(
            error=str(e),
            message="Failed to retrieve document",
            status_code=400
        )
    finally:
        db.close()

@command_handler(ListDocumentsQuery)
async def handle_list_documents(query: ListDocumentsQuery) -> CommandResponse[List[Dict[str, Any]]]:
    """Handle listing documents with optional filtering."""
    db = SessionLocal()
    try:
        # Start with base query
        q = db.query(DocumentModel).filter(DocumentModel.deleted_by.is_(None))
        
        # Apply filters
        if query.document_type:
            q = q.filter(DocumentModel.document_type == query.document_type)
        if query.created_by:
            q = q.filter(DocumentModel.created_by == str(query.created_by))
        
        # Apply sorting
        sort_field = getattr(DocumentModel, query.sort_by, None)
        if sort_field is not None:
            if query.sort_order.lower() == "desc":
                sort_field = sort_field.desc()
            q = q.order_by(sort_field)
        
        # Apply pagination
        total = q.count()
        documents = q.offset(query.skip).limit(query.limit).all()
        
        return CommandResponse.success(
            data=[doc.to_dict() for doc in documents],
            message=f"Found {len(documents)} documents",
            status_code=200
        )
    except Exception as e:
        return CommandResponse.error(
            error=str(e),
            message="Failed to list documents",
            status_code=400
        )
    finally:
        db.close()

@command_handler(SearchDocumentsQuery)
async def handle_search_documents(query: SearchDocumentsQuery) -> CommandResponse[List[Dict[str, Any]]]:
    """Handle document search."""
    db = SessionLocal()
    try:
        # This is a simple search implementation
        # In a real app, you'd use full-text search or a search engine
        q = db.query(DocumentModel).filter(
            DocumentModel.deleted_by.is_(None),
            (
                DocumentModel.content.ilike(f"%{query.query}%") |
                DocumentModel.title.ilike(f"%{query.query}%")
            )
        )
        
        if query.document_type:
            q = q.filter(DocumentModel.document_type == query.document_type)
        
        total = q.count()
        documents = q.offset(query.skip).limit(query.limit).all()
        
        return CommandResponse.success(
            data=[doc.to_dict() for doc in documents],
            message=f"Found {len(documents)} matching documents",
            status_code=200
        )
    except Exception as e:
        return CommandResponse.error(
            error=str(e),
            message="Failed to search documents",
            status_code=400
        )
    finally:
        db.close()
