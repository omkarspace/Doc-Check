from app.database.database import SessionLocal, engine
from app.models.user import User, UserRole
from passlib.context import CryptContext

def create_test_user():
    db = SessionLocal()
    
    # Test user details
    test_user = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "role": UserRole.USER
    }
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == test_user["email"]).first()
    if existing_user:
        print(f"User with email {test_user['email']} already exists")
        print(f"Username: {existing_user.username}")
        print("You can use these credentials to log in.")
        return
    
    # Create new user
    try:
        db_user = User(
            email=test_user["email"],
            username=test_user["username"],
            role=test_user["role"]
        )
        db_user.set_password(test_user["password"])
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        print("Test user created successfully!")
        print(f"Email: {test_user['email']}")
        print(f"Password: {test_user['password']}")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating test user: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
