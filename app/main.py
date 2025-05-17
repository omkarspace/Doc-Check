from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
from app.database import init_db
from app.middleware.static_files import setup_static_files
from app.utils.monitoring import Monitoring
from app.security import get_current_user
from app.api.v1 import api as v1_api
import logging
import time

app = FastAPI(
    title="DocuGenie - Intelligent Document Processing",
    description="AI-powered document processing platform for BFSI institutions",
    version=settings.VERSION,
    openapi_url="/api/v1/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize monitoring
monitoring = Monitoring()
monitoring.setup_metrics(app)
app = monitoring.setup_sentry(app)

# Add request monitoring middleware
@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    monitoring.track_active_request()
    
    response = await call_next(request)
    
    processing_time = time.time() - start_time
    monitoring.track_document_processing(
        document_type="unknown",
        status=str(response.status_code),
        processing_time=processing_time
    )
    
    return response

# Setup static files
app = setup_static_files(app)

# Initialize database
init_db()

# Include API routers
app.include_router(v1_api.router, prefix="/api/v1")

@app.get("/")
async def read_root(user: str = Depends(get_current_user)):
    return {"message": "Welcome to DocuGenie - Intelligent Document Processing Platform"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
