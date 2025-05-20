from sqlalchemy import create_engine, text
from app.security.auth import get_password_hash
import os

# Database URL - adjust if needed
DATABASE_URL = "sqlite:///./docugenie.db"
engine = create_engine(DATABASE_URL)

def create_test_user():
    with engine.connect() as conn:
        # Check if users table exists
        result = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        )
        if not result.fetchone():
            print("Users table doesn't exist. Creating table...")
            conn.execute(text("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    username VARCHAR(255) NOT NULL UNIQUE,
                    hashed_password VARCHAR(255) NOT NULL,
                    full_name VARCHAR(255),
                    role VARCHAR(50) DEFAULT 'user',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);
                CREATE INDEX IF NOT EXISTS ix_users_username ON users(username);
            """))
            conn.commit()

        # Check if test user exists
        test_email = "test@example.com"
        result = conn.execute(
            text("SELECT email FROM users WHERE email = :email"),
            {"email": test_email}
        )
        
        if result.fetchone():
            print("Test user already exists:")
            print(f"Email: {test_email}")
            print("Password: testpassword123")
            return
            
        # Create test user
        hashed_password = get_password_hash("testpassword123")
        conn.execute(
            text("""
                INSERT INTO users (email, username, hashed_password, role, is_active)
                VALUES (:email, :username, :hashed_password, :role, :is_active)
            """),
            {
                "email": test_email,
                "username": "testuser",
                "hashed_password": hashed_password,
                "role": "user",
                "is_active": 1
            }
        )
        conn.commit()
        
        print("Test user created successfully!")
        print(f"Email: {test_email}")
        print("Password: testpassword123")

if __name__ == "__main__":
    create_test_user()
