from fastapi import APIRouter, Depends, status

# OAuth2PasswordRequestForm provides the standard username/password
# fields used by FastAPI's OAuth2 password authentication flow.
from fastapi.security import OAuth2PasswordRequestForm

from models import schemas
from services import auth_service

# Creates the router used for authentication-related endpoints.
router = APIRouter()


# Registers a new user account.
#
# The request body contains the user's email, password, role,
# and branch information.
@router.post(
    "/register",
    response_model=schemas.TokenResponse,
    status_code=status.HTTP_201_CREATED
)
def register(payload: schemas.RegisterRequest):

    # Passes the registration information to the service layer.
    # The service handles creating the user and generating tokens.
    return auth_service.register_user(
        email=payload.email,
        password=payload.password,
        role=payload.role,
        branch_id=payload.branch_id,
    )


# Logs an existing user into the application.
#
# OAuth2PasswordRequestForm provides the username and password
# submitted by the client. In this application, the username
# field is used to submit the user's email.
@router.post(
    "/login",
    response_model=schemas.TokenResponse
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):

    # Sends the submitted email and password to the authentication
    # service, which verifies the credentials and creates tokens.
    return auth_service.login_user(
        email=form_data.username,
        password=form_data.password
    )