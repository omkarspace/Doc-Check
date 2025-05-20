from sqlalchemy import create_engine, text
from app.security.auth import verify_password

# Database URL - adjust if needed
DATABASE_URL = "sqlite:///./docugenie.db"
engine = create_engine(DATABASE_URL)

def check_test_user():
    with engine.connect() as conn:
        # Get the test user
        result = conn.execute(
            text("SELECT email, hashed_password FROM users WHERE email = :email"),
            {"email": "test@example.com"}
        )
        
        user = result.fetchone()
        if not user:
            print("Test user not found in the database")
            return
            
        email, hashed_password = user
        print(f"Found user: {email}")
        print(f"Password hash: {hashed_password}")
        
        # Try to verify the password
        is_valid = verify_password("testpassword123", hashed_password)
        print(f"Password verification: {'SUCCESS' if is_valid else 'FAILED'}")

if __name__ == "__main__":
    check_test_user()
