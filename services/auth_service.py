import uuid

from fastapi import HTTPException
from sqlalchemy import select

from models.database import SessionLocal, User
from security.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token
)


ALLOWED_ROLES = {
    "CUSTOMER",
    "TELLER",
    "BRANCH_MANAGER",
    "ADMIN"
}


def register_user(
    email: str,
    password: str,
    role: str = "CUSTOMER"
):
    """Create a new authenticated user."""

    if role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=400,
            detail="Invalid role"
        )

    db = SessionLocal()

    try:
        existing_user = db.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email is already registered"
            )

        user = User(
            id=str(uuid.uuid4())[:8],
            email=email,
            password_hash=hash_password(password),
            role=role,
            active=True
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        access_token = create_access_token(
            user.id,
            user.email,
            user.role
        )

        refresh_token = create_refresh_token(
            user.id,
            user.email,
            user.role
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    finally:
        db.close()


def login_user(
    email: str,
    password: str
):
    """Authenticate a user and issue JWT tokens."""

    db = SessionLocal()

    try:
        user = db.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        if not user.active:
            raise HTTPException(
                status_code=401,
                detail="User account is inactive"
            )

        if not verify_password(
            password,
            user.password_hash
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        access_token = create_access_token(
            user.id,
            user.email,
            user.role
        )

        refresh_token = create_refresh_token(
            user.id,
            user.email,
            user.role
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    finally:
        db.close()