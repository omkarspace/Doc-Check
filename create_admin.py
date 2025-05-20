import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent))

from app.database.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

def create_admin_user():
    db = SessionLocal()
    try:
        admin_email = "admin@example.com"
        admin = db.query(User).filter(User.email == admin_email).first()
        
        if not admin:
            admin = User(
                email=admin_email,
                username="admin",
                hashed_password=get_password_hash("admin123"),
                full_name="Admin User",
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin)
            db.commit()
            print(f"✅ Created default admin user with email: {admin_email} and password: admin123")
        else:
            # Update password to ensure it's set correctly
            admin.hashed_password = get_password_hash("admin123")
            admin.is_active = True
            db.commit()
            print(f"✅ Reset password for existing admin user: {admin_email}")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
