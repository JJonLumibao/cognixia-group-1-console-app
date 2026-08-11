from fastapi import APIRouter, status

from models.schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse
)

from services.auth_service import (
    register_user,
    login_user
)


router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
def register(payload: RegisterRequest):

    """Register a new user account."""

    user = register_user(
        email=payload.email,
        password=payload.password,
        role=payload.role
    )

    return {
        "id": user.id,
        "email": user.email,
        "role": user.role
    }


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK
)
def login(payload: LoginRequest):

    """Authenticate a user and return JWT tokens."""

    return login_user(
        email=payload.email,
        password=payload.password
    )