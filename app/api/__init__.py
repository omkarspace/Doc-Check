from fastapi import APIRouter
from app.api.v1 import api as v1_api

# Create the main API router
api_router = APIRouter()

# Include the version 1 API router
api_router.include_router(v1_api.router, prefix="/v1")
