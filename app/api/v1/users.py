from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.user import User
from app.models.schemas import UserCreate, UserInDB, UserInResponse, UserRole
from app.security.auth import get_current_active_user, get_password_hash

router = APIRouter()

@router.get("/", response_model=List[UserInResponse], tags=["users"])
async def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve all users (admin only)
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.post("/", response_model=UserInResponse, status_code=status.HTTP_201_CREATED, tags=["users"])
async def create_user(
    user: UserCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new user (admin only)
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if user already exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password
    hashed_password = get_password_hash(user.password)
    
    # Create new user
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_active=user.is_active if hasattr(user, 'is_active') else True,
        is_superuser=user.is_superuser if hasattr(user, 'is_superuser') else False,
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/me", response_model=UserInResponse, tags=["users"])
async def read_user_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user
    """
    return current_user

@router.get("/{user_id}", response_model=UserInResponse, tags=["users"])
async def read_user(
    user_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific user by ID
    """
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user
