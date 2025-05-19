from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

from ...mcp import Command

class CreateDocumentCommand(Command):
    """Command to create a new document."""
    title: str
    content: str
    document_type: str
    metadata: Optional[Dict[str, Any]] = {}
    created_by: UUID

class UpdateDocumentCommand(Command):
    """Command to update an existing document."""
    document_id: UUID
    title: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    updated_by: UUID

class DeleteDocumentCommand(Command):
    """Command to delete a document."""
    document_id: UUID
    deleted_by: UUID
