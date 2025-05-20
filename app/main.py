from fastapi import FastAPI, HTTPException, Depends, Request, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path
import os
import logging

from app.config import settings
from app.database import init_db, get_db
from app.utils.monitoring import Monitoring, setup_monitoring
from app.models.user import User
from app.schemas.token import TokenData
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.api.v1 import router as api_router
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

# Initialize FastAPI app
app = FastAPI(
    title="DocuGenie - Intelligent Document Processing",
    description="AI-powered document processing platform for BFSI institutions",
    version=settings.VERSION,
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    debug=settings.DEBUG
)

# Add GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Set up paths
BASE_DIR = Path(__file__).parent  # This points to /app
frontend_dir = BASE_DIR / "frontend"  # Now points to /app/frontend
templates_dir = frontend_dir / "templates"
static_dir = frontend_dir / "static"

# Ensure directories exist
templates_dir.mkdir(parents=True, exist_ok=True)
static_dir.mkdir(parents=True, exist_ok=True)

# Set up templates
templates = Jinja2Templates(directory=str(templates_dir))

# Add template globals
templates.env.globals.update({
    'settings': settings,
    'now': datetime.utcnow
})

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

# Initialize monitoring
try:
    monitoring = Monitoring()
    monitoring.setup_metrics(app)
    app = monitoring.setup_sentry(app)
except Exception as e:
    logging.warning(f"Monitoring setup failed: {e}")
    monitoring = None

# Mount static files
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Initialize monitoring
monitoring = None
try:
    monitoring = Monitoring()
    setup_monitoring(app)
except Exception as e:
    logging.warning(f"Monitoring setup failed: {e}")

# Add request monitoring middleware
@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    
    # Only track if monitoring is initialized
    if monitoring:
        try:
            monitoring.track_active_request()
        except Exception as e:
            logging.warning(f"Error tracking active request: {e}")
    
    response = await call_next(request)
    
    if monitoring:
        try:
            processing_time = time.time() - start_time
            monitoring.track_document_processing(
                document_type="unknown",
                status=str(response.status_code),
                processing_time=processing_time
            )
        except Exception as e:
            logging.warning(f"Error tracking document processing: {e}")
    
    return response

# Initialize database
init_db()

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Serve frontend files
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_root(request: Request):
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logging.error(f"Error serving frontend: {e}")
        return HTMLResponse("""
            <html>
                <head><title>DocuGenie</title></head>
                <body>
                    <h1>Welcome to DocuGenie</h1>
                    <p>The application is running, but the frontend is not properly configured.</p>
                    <p>Please <a href="/login">login</a> to continue.</p>
                    <p>API documentation is available at <a href="/api/docs">/api/docs</a></p>
                </body>
            </html>
        """)

# Login route
@app.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def login_page(request: Request):
    try:
        # Check if template exists
        template_path = templates_dir / "auth" / "login.html"
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
            
        # Check if static files are accessible
        static_files = ["js/auth.js", "css/styles.css"]
        for static_file in static_files:
            static_path = static_dir / static_file
            if not static_path.exists():
                logger.warning(f"Static file not found: {static_path}")
        
        return templates.TemplateResponse("auth/login.html", {
            "request": request, 
            "title": "Login - DocuGenie",
            "static_url": "/static"
        })
    except Exception as e:
        logger.error(f"Error loading login page: {str(e)}", exc_info=True)
        return HTMLResponse(f"""
            <html>
                <head><title>Error</title></head>
                <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #dc3545;">Error loading login page</h1>
                    <div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 4px; margin: 15px 0;">
                        <p><strong>Error:</strong> {str(e)}</p>
                    </div>
                    <h2>Debug Information:</h2>
                    <ul>
                        <li>Template directory: {templates_dir}</li>
                        <li>Static directory: {static_dir}</li>
                        <li>Login template exists: {"Yes" if (templates_dir / "auth" / "login.html").exists() else "No"}</li>
                    </ul>
                    <p>Please check the server logs for more details.</p>
                </body>
            </html>
        """.format(e=e, templates_dir=templates_dir, static_dir=static_dir))

# Dashboard route
@app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def dashboard_page(request: Request):
    return await serve_frontend(request)

# Serve frontend files
async def serve_frontend(request: Request):
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logger.error(f"Error serving frontend: {e}")
        return HTMLResponse("""
            <html>
                <head><title>DocuGenie</title></head>
                <body>
                    <h1>Welcome to DocuGenie</h1>
                    <p>The application is running, but the frontend is not properly configured.</p>
                    <p>Please <a href="/login">login</a> to continue.</p>
                    <p>API documentation is available at <a href="/api/docs">/api/docs</a></p>
                </body>
            </html>
        """)

# Catch-all route for SPA routing
@app.get("/{full_path:path}", include_in_schema=False)
async def catch_all(request: Request, full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    return await serve_frontend(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
