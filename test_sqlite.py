import sys
from pathlib import Path
from sqlalchemy import create_engine, text

# Add the project root to the Python path
project_root = str(Path(__file__).parent.absolute())
sys.path.insert(0, project_root)

# Import settings
from app.config.settings import get_settings

# Get settings instance
settings = get_settings()

def test_sqlite_connection():
    # Get the database URL from settings
    db_url = settings.SQLALCHEMY_DATABASE_URI
    print(f"Using database URL: {db_url}")
    
    # Configure connection arguments for SQLite
    connect_args = {}
    if db_url.startswith('sqlite'):
        connect_args = {'check_same_thread': False}
    
    try:
        # Create engine
        engine = create_engine(db_url, connect_args=connect_args)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 'SQLite connection successful' as status"))
            print(result.scalar())
            
        print("SQLite connection test passed!")
        return True
        
    except Exception as e:
        print(f"Error connecting to SQLite: {e}")
        return False

if __name__ == "__main__":
    test_sqlite_connection()
