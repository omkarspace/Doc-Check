import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.absolute())
sys.path.insert(0, project_root)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import Settings

# Initialize settings
settings = Settings()

# Get database URL
DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI
print(f"Using database URL: {DATABASE_URL}")

# For SQLite, we need to set check_same_thread to False
connect_args = {}
if DATABASE_URL.startswith('sqlite'):
    connect_args = {'check_same_thread': False}
    print("Using SQLite database")

# Create engine
try:
    engine = create_engine(
        DATABASE_URL,
        connect_args=connect_args,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    
    # Test connection
    with engine.connect() as connection:
        print("Successfully connected to the database!")
        
    # Create a session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Import models to register them with SQLAlchemy
    from app import models
    from sqlalchemy.ext.declarative import declarative_base
    
    # Create tables
    Base = declarative_base()
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    
except Exception as e:
    print(f"Error: {e}")
    raise e
