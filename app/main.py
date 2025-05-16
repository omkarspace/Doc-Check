from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
from app.api import api_router
from app.database import init_db
from app.middleware.static_files import setup_static_files
from app.utils.monitoring import setup_monitoring

app = FastAPI(
    title="DocuGenie - Intelligent Document Processing",
    description="AI-powered document processing platform for BFSI institutions",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup monitoring
app = setup_monitoring(app)

# Setup static files
app = setup_static_files(app)

# Initialize database
init_db()

# Include API router
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to DocuGenie - Intelligent Document Processing Platform"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
