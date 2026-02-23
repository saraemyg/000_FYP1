"""Authentication API endpoints."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_admin_user, get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models import User
from app.schemas import Token, UserCreate, UserLogin, UserResponse

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
) -> Token:
    """
    Authenticate user and return JWT token.

    Args:
        credentials: Login credentials
        db: Database session

    Returns:
        JWT access token
    """
    # Find user by username
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    # Update last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()

    # Create access token
    access_token = create_access_token(data={"sub": user.username})

    return Token(access_token=access_token)


@router.post("/register", response_model=UserResponse)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
) -> User:
    """
    Register a new user (admin only).

    Args:
        user_data: New user data
        db: Database session
        current_admin: Current admin user

    Returns:
        Created user
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current authenticated user info.

    Args:
        current_user: Current authenticated user

    Returns:
        User information
    """
    return current_user


@router.get("/users", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
    skip: int = 0,
    limit: int = 100,
) -> list[User]:
    """
    List all users (admin only).

    Args:
        db: Database session
        current_admin: Current admin user
        skip: Number of records to skip
        limit: Maximum number of records

    Returns:
        List of users
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.put("/users/{user_id}/toggle-active", response_model=UserResponse)
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user),
) -> User:
    """
    Toggle user active status (admin only).

    Args:
        user_id: User ID to toggle
        db: Database session
        current_admin: Current admin user

    Returns:
        Updated user
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Prevent admin from disabling themselves
    if user.user_id == current_admin.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot disable your own account",
        )

    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)

    return user
