from fastapi import APIRouter

# Import all API endpoints
from app.api.v1 import auth, users, documents, document_versions, templates, batches, export, dashboard

# Create the v1 API router
router = APIRouter()

# Include all API endpoints
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(documents.router, prefix="/documents", tags=["Documents"])
router.include_router(document_versions.router, prefix="/document-versions", tags=["Document Versions"])
router.include_router(templates.router, prefix="/templates", tags=["Templates"])
router.include_router(batches.router, prefix="/batches", tags=["Batches"])
router.include_router(export.router, prefix="/export", tags=["Export"])
router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
