from fastapi import APIRouter, status, HTTPException, Depends

from models import schemas
from security.dependencies import get_current_user, require_roles
from services import branch_manager_service

# Creates the router used for branch and branch-manager endpoints.
router = APIRouter()


# Retrieves all branches.
#
# This endpoint is useful for viewing branch information across
# the bank, including branch performance and staff metrics.
@router.get(
    "/branches",
    response_model=list[schemas.BranchResponse],
    status_code=status.HTTP_200_OK
)
def get_branches(
    current_user=Depends(get_current_user)
):
    # Calls the service responsible for retrieving all branches.
    return branch_manager_service.get_all_branches()


# Retrieves performance information for the branch assigned
# to the currently authenticated branch manager.
#
# The service determines which branch belongs to the logged-in
# branch manager using the user's information from the JWT.
@router.get("/branch-performance")
def get_branch_performance(
    current_user=Depends(require_roles("BRANCH_MANAGER"))
):
    return branch_manager_service.get_branch_performance(current_user)


# Retrieves staff metrics for the branch assigned to the
# currently authenticated branch manager.
#
# Metrics include information such as total staff and
# the number of tellers assigned to the branch.
@router.get("/staff-metrics")
def get_staff_metrics(
    current_user=Depends(require_roles("BRANCH_MANAGER"))
):
    return branch_manager_service.get_staff_metrics(current_user)


# Creates a new branch.
#
# Only administrators are allowed to create branches.
@router.post(
    "/branches",
    response_model=schemas.BranchResponse,
    status_code=status.HTTP_201_CREATED
)
def create_branch(
    payload: schemas.BranchCreate,
    current_user=Depends(require_roles("ADMIN"))
):
    try:
        # Converts the Pydantic request model into a dictionary
        # before passing it to the service layer.
        return branch_manager_service.create_branch(
            payload.model_dump()
        )

    # Converts service-level ValueErrors into an HTTP 400 response.
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Assigns or changes the manager responsible for a branch.
#
# Only administrators are allowed to change branch managers.
#
# The branch is identified by branch_code in the URL, while
# the new manager's user ID is provided in the request body.
@router.patch(
    "/{branch_code}/manager",
    response_model=schemas.BranchResponse,
    status_code=status.HTTP_200_OK
)
def update_branch_manager(
    branch_code: str,
    payload: schemas.BranchManagerUpdate,
    current_user=Depends(require_roles("ADMIN"))
):
    try:
        # Passes the branch code and new manager ID to the
        # service layer to perform the assignment.
        return branch_manager_service.update_branch_manager(
            branch_code,
            payload.manager_id
        )

    # Converts service-level ValueErrors into an HTTP 404 response.
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )