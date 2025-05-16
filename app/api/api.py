from fastapi import APIRouter
from app.api.v1 import document, user, auth

api_router = APIRouter()

# Include API version 1 routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(document.router, prefix="/documents", tags=["documents"])
