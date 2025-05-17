from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os

def setup_static_files(app: FastAPI) -> FastAPI:
    """
    Setup static file serving for the FastAPI application.
    
    Args:
        app: The FastAPI application instance
        
    Returns:
        FastAPI: The configured FastAPI application
    """
    # Create static directory if it doesn't exist
    static_dir = Path("static")
    static_dir.mkdir(exist_ok=True)
    
    # Mount the static files directory
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    # Add CORS middleware to allow static file access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app
