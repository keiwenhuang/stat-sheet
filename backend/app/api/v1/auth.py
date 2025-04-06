from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from backend.app.db.database import get_db
from backend.app.db.models.auth import User, Role
from backend.app.schemas.auth import (
    UserCreate,
    UserResponse,
    UserUpdate,
    Token,
    RoleCreate,
    RoleResponse,
)
from backend.app.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_admin_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Login and get access token"""
    # Find user
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # Get user scopes from roles
    scopes = []
    for role in user.roles:
        if role.name.lower() == "admin":
            scopes.append("admin")
        elif role.name.lower() == "league_manager":
            scopes.append("league_manager")
        elif role.name.lower() == "stat_keeper":
            scopes.append("stat_keeper")

    # Create token with scopes
    access_token = create_access_token(
        data={"sub": user.username, "scopes": scopes},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    user_create: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Register a new user (admin only)"""
    # Check if username or email already exists
    existing_user = (
        db.query(User)
        .filter(
            (User.username == user_create.username) | (User.email == user_create.email)
        )
        .first()
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    # Create new user
    hashed_password = get_password_hash(user_create.password)
    new_user = User(
        username=user_create.username,
        email=user_create.email,
        password_hash=hashed_password,
        is_active=user_create.is_active,
    )

    # Add roles
    if user_create.role_ids:
        roles = db.query(Role).filter(Role.id.in_(user_create.role_ids)).all()
        new_user.roles = roles

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/roles", response_model=List[RoleResponse])
async def get_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Get all available roles (admin only)"""
    roles = db.query(Role).all()
    return roles


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_create: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """Create a new role (admin only)"""
    # Check if role name already exists
    existing_role = db.query(Role).filter(Role.name == role_create.name).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role name already exists",
        )

    # Create new role
    new_role = Role(**role_create.model_dump())
    db.add(new_role)
    db.commit()
    db.refresh(new_role)

    return new_role
