import os
import bcrypt
from jose import jwt

from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv


# ENVIRONMENT CONFIGURATION
# Load security-related environment variables from the .env file.
load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")

# The application cannot create or validate JWTs without a secret key.
if not JWT_SECRET:
    raise ValueError(
        "JWT_SECRET is missing. Please ensure your .env file is set up."
    )


# JWT CONFIGURATION
# HS256 is used to sign and verify the application's JWT tokens.
JWT_ALGORITHM = "HS256"

# Access tokens are short-lived because they are used for API authentication.
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Refresh tokens remain valid longer and can be used to obtain new access tokens.
REFRESH_TOKEN_EXPIRE_DAYS = 7


# PASSWORD SECURITY
# Hash a user's password before storing it in the database.
def hash_password(password: str) -> str:

    # Generate a unique salt for the password.
    salt = bcrypt.gensalt()

    # Hash the password with bcrypt and return it as a string.
    return bcrypt.hashpw(
        password.encode("utf-8"),
        salt
    ).decode("utf-8")


# PASSWORD VERIFICATION
# Check whether a plain-text password matches a stored bcrypt hash.
def verify_password(
    password: str,
    password_hash: str
) -> bool:

    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    )


# ACCESS TOKEN CREATION
# Create a short-lived JWT used to authenticate API requests.
def create_access_token(
    user_id: str,
    email: str,
    role: str,
    branch_id: str | None = None
) -> str:

    # Use the current UTC time as the starting point for the token.
    now = datetime.now(timezone.utc)

    # Store the user's authentication and authorization information
    # inside the JWT payload.
    payload = {
        "sub": user_id,
        "email": email,
        "roles": [role],
        "branch_id": branch_id,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    }

    # Sign the JWT using the application's secret and configured algorithm.
    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )


# REFRESH TOKEN CREATION
# Create a longer-lived JWT that can be used to obtain a new access token.
def create_refresh_token(
    user_id: str,
    email: str,
    role: str,
    branch_id: str | None = None
) -> str:

    # Use the current UTC time as the starting point for the token.
    now = datetime.now(timezone.utc)

    # Store the user's information and identify this token as a refresh token.
    payload = {
        "sub": user_id,
        "email": email,
        "roles": [role],
        "branch_id": branch_id,
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS
        )
    }

    # Sign the refresh token using the application's JWT secret.
    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )


# TOKEN VALIDATION
# Decode a JWT and verify that it was signed correctly and has not expired.
def decode_token(token: str) -> dict:

    try:
        # Decode the token using the application's secret and algorithm.
        # This also validates the token's expiration time.
        return jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

    # Convert JWT expiration errors into a ValueError that
    # the authentication dependency can handle.
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")

    # Convert other JWT validation errors into a generic ValueError.
    except jwt.JWTError:
        raise ValueError("Invalid token")