from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from models import schemas
from services import auth_service

router = APIRouter()


@router.post(
    "/register",
    response_model=schemas.TokenResponse,
    status_code=status.HTTP_201_CREATED
)
def register(payload: schemas.RegisterRequest):
    return auth_service.register_user(
        email=payload.email,
        password=payload.password,
        role=payload.role
    )


@router.post(
    "/login",
    response_model=schemas.TokenResponse
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    return auth_service.login_user(
        email=form_data.username,
        password=form_data.password
    )