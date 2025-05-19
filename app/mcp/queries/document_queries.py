from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

from ...mcp import Query

class GetDocumentQuery(Query):
    """Query to get a document by ID."""
    document_id: UUID

class ListDocumentsQuery(Query):
    """Query to list documents with optional filtering and pagination."""
    skip: int = 0
    limit: int = 100
    document_type: Optional[str] = None
    created_by: Optional[UUID] = None
    sort_by: Optional[str] = "created_at"
    sort_order: str = "desc"

class SearchDocumentsQuery(Query):
    """Query to search documents by content or metadata."""
    query: str
    document_type: Optional[str] = None
    skip: int = 0
    limit: int = 100
