import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.append(str(Path(__file__).parent.parent))

from app.database.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

def create_admin_user(email: str, password: str, username: str = "admin"):
    """Create an admin user if it doesn't exist."""
    db = SessionLocal()
    try:
        # Check if admin already exists
        admin = db.query(User).filter(User.email == email).first()
        if admin:
            print(f"Admin user with email {email} already exists.")
            return False
            
        # Create new admin user
        admin = User(
            email=email,
            username=username,
            hashed_password=get_password_hash(password),
            full_name="Admin User",
            role=UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"Admin user created successfully with email: {email}")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"Error creating admin user: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    import getpass
    
    print("Create Admin User")
    print("=================")
    
    email = input("Enter admin email (default: admin@example.com): ") or "admin@example.com"
    username = input(f"Enter username (default: admin): ") or "admin"
    
    while True:
        password = getpass.getpass("Enter password: ")
        if not password:
            print("Password cannot be empty. Please try again.")
            continue
            
        confirm_password = getpass.getpass("Confirm password: ")
        if password != confirm_password:
            print("Passwords do not match. Please try again.")
        else:
            break
    
    create_admin_user(email, password, username)
