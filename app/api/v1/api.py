from fastapi import APIRouter

# Create the v1 API router
router = APIRouter()

# Import and include routers directly
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.documents import router as documents_router
from app.api.v1.document_versions import router as document_versions_router
from app.api.v1.templates import router as templates_router
from app.api.v1.batches import router as batches_router
from app.api.v1.export import router as export_router
from app.api.v1.dashboard import router as dashboard_router

# Include all API endpoints
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(users_router, prefix="/users", tags=["Users"])
router.include_router(documents_router, prefix="/documents", tags=["Documents"])
router.include_router(document_versions_router, prefix="/document-versions", tags=["Document Versions"])
router.include_router(templates_router, prefix="/templates", tags=["Templates"])
router.include_router(batches_router, prefix="/batches", tags=["Batches"])
router.include_router(export_router, prefix="/export", tags=["Export"])
router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
