from fastapi import HTTPException
from sqlalchemy import select

from models.database import SessionLocal, User, generate_id
from security.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token
)


# VALID USER ROLES
# These are the roles that can be assigned when registering a user.
ALLOWED_ROLES = {
    "CUSTOMER",
    "TELLER",
    "BRANCH_MANAGER",
    "ADMIN"
}


# USER REGISTRATION
# Create a new user account and issue authentication tokens.
def register_user(
    email: str,
    password: str,
    role: str = "CUSTOMER",
    branch_id: str | None = None
):
    """Create a new authenticated user."""

    # Make sure the requested role is one of the supported roles.
    if role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=400,
            detail="Invalid role"
        )

    # Open a database session.
    db = SessionLocal()

    try:
        # Check whether another user is already registered with this email.
        existing_user = db.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email is already registered"
            )

        # Create the new user record.
        user = User(
            id=generate_id(),
            email=email,
            password_hash=hash_password(password),
            role=role,
            branch_id=branch_id,
            active=True
        )

        # Save the user to the database.
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create a short-lived access token for the new user.
        access_token = create_access_token(
            user.id,
            user.email,
            user.role,
            branch_id=user.branch_id
        )

        # Create a longer-lived refresh token.
        refresh_token = create_refresh_token(
            user.id,
            user.email,
            user.role,
            branch_id=user.branch_id
        )

        # Return both tokens to the client.
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    # Always close the database connection after the operation.
    finally:
        db.close()


# USER LOGIN
# Authenticate an existing user and issue new JWT tokens.
def login_user(
    email: str,
    password: str
):
    """Authenticate a user and issue JWT tokens."""

    # Open a database session.
    db = SessionLocal()

    try:
        # Find the user by their email address.
        user = db.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

        # Reject the login if the email does not exist.
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        # Inactive users are not allowed to log in.
        if not user.active:
            raise HTTPException(
                status_code=401,
                detail="User account is inactive"
            )

        # Compare the submitted password with the stored bcrypt hash.
        if not verify_password(
            password,
            user.password_hash
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        # Create a short-lived access token.
        access_token = create_access_token(
            user.id,
            user.email,
            user.role,
            branch_id=user.branch_id
        )

        # Create a longer-lived refresh token.
        refresh_token = create_refresh_token(
            user.id,
            user.email,
            user.role,
            branch_id=user.branch_id
        )

        # Return both tokens to the client.
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    # Always close the database connection after the operation.
    finally:
        db.close()