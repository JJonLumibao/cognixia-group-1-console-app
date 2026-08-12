from fastapi import APIRouter, Depends, status
from typing import List

from models import schemas
from services import user_service
from security.dependencies import require_roles


router = APIRouter()


@router.get(
    "",
    response_model=List[schemas.UserResponse],
    status_code=status.HTTP_200_OK
)
def get_users(
    current_user=Depends(require_roles("ADMIN"))
):
    return user_service.get_all_users()