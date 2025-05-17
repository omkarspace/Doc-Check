from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from app.config.settings import Settings
import os

settings = Settings()

# Get database URL from settings
DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI

# For SQLite, we need to set check_same_thread to False
connect_args = {}
if DATABASE_URL.startswith('sqlite'):
    connect_args = {'check_same_thread': False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=3600
)

# Create a scoped session factory
SessionLocal = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)

# Base class for all models
Base = declarative_base()

def get_db():
    """
    Dependency function that yields db sessions
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize the database by creating all tables
    """
    import app.models  # Import all models to register them with SQLAlchemy
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized at: {DATABASE_URL}")
