from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from security.security import decode_token


# OAUTH2 CONFIGURATION
# Defines where FastAPI should send users when obtaining an OAuth2 access token.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


# AUTHENTICATION
# Extract and validate the currently authenticated user from their JWT.
def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    # Attempt to decode and validate the JWT.
    try:
        payload = decode_token(token)

    # Reject the request if the token is invalid or has expired.
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # Only access tokens can be used to access protected API endpoints.
    # Refresh tokens cannot be used as authentication credentials.
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # Return the decoded JWT payload so endpoints can access
    # information such as the user's ID, email, roles, and branch.
    return payload


# ROLE-BASED AUTHORIZATION
# Restrict an endpoint so that only users with specific roles can access it.
def require_roles(*allowed_roles):

    # Dependency function used by FastAPI to check the user's roles.
    def role_checker(
        current_user=Depends(get_current_user)
    ):
        # Get the roles stored in the authenticated user's JWT.
        user_roles = current_user.get("roles", [])

        # Check whether the user has at least one of the roles
        # allowed to access the endpoint.
        if not any(role in allowed_roles for role in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )

        # Return the authenticated user so the endpoint can use
        # their information after authorization succeeds.
        return current_user

    # Return the dependency function to FastAPI.
    return role_checker