from fastapi import APIRouter
from . import __all__ as endpoints

# Create the v1 API router
router = APIRouter()

# Import all endpoints to register their routes
from . import auth, users, documents, document_versions, templates, batches, export, dashboard

# Include all API endpoints
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(documents.router, prefix="/documents", tags=["Documents"])
router.include_router(document_versions.router, prefix="/document-versions", tags=["Document Versions"])
router.include_router(templates.router, prefix="/templates", tags=["Templates"])
router.include_router(batches.router, prefix="/batches", tags=["Batches"])
router.include_router(export.router, prefix="/export", tags=["Export"])
router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
