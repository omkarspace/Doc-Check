from app.database.database import SessionLocal, init_db
from app.models.user import User, UserRole
from app.security.auth import get_password_hash

def create_test_user():
    db = SessionLocal()
    try:
        # Check if user already exists
        test_email = "test@example.com"
        existing_user = db.query(User).filter(User.email == test_email).first()
        
        if existing_user:
            print("Test user already exists:")
            print(f"Email: {test_email}")
            print("Password: testpassword123")
            return
            
        # Create test user
        hashed_password = get_password_hash("testpassword123")
        test_user = User(
            email=test_email,
            username="testuser",
            hashed_password=hashed_password,
            role=UserRole.USER
        )
        
        db.add(test_user)
        db.commit()
        
        print("Test user created successfully!")
        print(f"Email: {test_email}")
        print("Password: testpassword123")
        
    except Exception as e:
        print(f"Error creating test user: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Initialize database tables
    print("Initializing database...")
    init_db()
    
    # Create test user
    print("\nCreating test user...")
    create_test_user()
