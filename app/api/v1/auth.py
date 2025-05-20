from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.security.auth import (
    verify_password,
    create_access_token,
    get_current_active_user,
    get_password_hash
)
from app.models.user import User
from app.database.database import SessionLocal
from app.config import settings

router = APIRouter(tags=["authentication"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class LoginRequest(BaseModel):
    username: str
    password: str
    remember_me: bool = False

@router.post("/login")
async def login_for_access_token(
    login_data: LoginRequest,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Login and get access token
    Accepts JSON with username/password
    """
    try:
        # Log request details
        if request:
            headers = dict(request.headers)
            print(f"\n=== New Login Request ===")
            print(f"Method: {request.method}")
            print(f"Headers: {headers}")
        
        # Get credentials from the validated request model
        username = login_data.username
        password = login_data.password
        remember_me = login_data.remember_me
        
        print(f"Login attempt - username: {username}, remember_me: {remember_me}")

        if not username or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username and password are required"
            )

        # Get user from database
        user = db.query(User).filter(User.email == username).first()
        if not user:
            print(f"User not found: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Check if user is active
        if not user.is_active:
            print(f"User account is disabled: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not user.verify_password(password):
            print(f"Invalid password for user: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        refresh_token = create_access_token(
            data={"sub": user.email}, expires_delta=refresh_token_expires
        ) if remember_me else None
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role
            }
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error during login: {str(e)}")
        import traceback
        traceback.print_exc()
        error_msg = "An error occurred during login"
        if "bcrypt" in str(e).lower():
            error_msg = "Error with password verification"
        elif "jwt" in str(e).lower():
            error_msg = "Error generating authentication token"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

@router.post("/register", tags=["authentication"])
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    """
    try:
        print(f"Received registration request for: {user_data.email}")
        
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        
        if existing_user:
            print(f"User {user_data.email} already exists")
            raise HTTPException(
                status_code=400,
                detail="Username or email already registered"
            )
        
        # Create new user
        print("Creating new user...")
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"User created successfully: {new_user.email}")
        
        return {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email
        }
        
    except Exception as e:
        db.rollback()
        print(f"Error in registration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during registration: {str(e)}"
        )

@router.get("/me", tags=["authentication"])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role
    }
