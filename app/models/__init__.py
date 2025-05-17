# Import all models to ensure they are registered with SQLAlchemy
from .user import User, UserRole
from .document import Document, DocumentType
from .document_version import DocumentVersion
from .template import Template, TemplateType
from .batch import Batch, BatchStatus

# This makes the models available when importing from app.models
__all__ = [
    'User', 'UserRole',
    'Document', 'DocumentType',
    'DocumentVersion',
    'Template', 'TemplateType',
    'Batch', 'BatchStatus'
]
