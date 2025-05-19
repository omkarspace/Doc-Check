# Import all handlers to ensure they're registered with the command bus
# Document handlers
from .document_handlers import (
    handle_create_document,
    handle_update_document,
    handle_delete_document,
    handle_get_document,
    handle_list_documents,
    handle_search_documents
)

__all__ = [
    'handle_create_document',
    'handle_update_document',
    'handle_delete_document',
    'handle_get_document',
    'handle_list_documents',
    'handle_search_documents'
]
