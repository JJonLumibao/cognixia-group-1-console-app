from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from security.security import decode_token


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme)
):
    """Extract and validate the current user from the JWT."""

    try:
        payload = decode_token(token)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    return payload

def require_roles(*allowed_roles):
    """Restrict an endpoint to specific roles."""

    def role_checker(
        current_user=Depends(get_current_user)
    ):
        user_roles = current_user.get("roles", [])

        if not any(role in allowed_roles for role in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        return current_user

    return role_checker