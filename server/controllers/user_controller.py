from fastapi import APIRouter, Depends, status
from typing import List

from models import schemas
from services import user_service
from security.dependencies import require_roles

# Creates the router used for user-related endpoints.
router = APIRouter()


# Retrieves all users in the system.
#
# This endpoint is restricted to administrators because user
# information should not be accessible to regular customers
# or other roles.
@router.get(
    "",
    response_model=List[schemas.UserResponse],
    status_code=status.HTTP_200_OK
)
def get_users(
    current_user=Depends(require_roles("ADMIN"))
):

    # Calls the service layer to retrieve all users.
    #
    # The service is responsible for querying the database
    # and returning the appropriate user information.
    return user_service.get_all_users()