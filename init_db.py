from app.database.database import init_db, Base, engine
from app.models.user import User, UserRole
from app.database.database import SessionLocal
from app.security.security import get_password_hash
from sqlalchemy.orm import sessionmaker
import os

# Import all models to ensure they are registered with SQLAlchemy
from app.models import user, document, document_version, template, batch

def create_admin_user():
    db = SessionLocal()
    try:
        # Check if admin user already exists
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            # Create admin user
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Admin User",
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists.")
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

def create_tables():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    # Create database tables
    print("Initializing database...")
    create_tables()
    
    # Create admin user
    print("Creating admin user...")
    create_admin_user()
    print("Database initialization complete!")
