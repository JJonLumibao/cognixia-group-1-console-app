from fastapi import APIRouter, status, HTTPException, Depends

from models import schemas
from security.dependencies import get_current_user
from services import branch_manager_service


router = APIRouter()

@router.get(
    "/branches",
    response_model=list[schemas.BranchResponse],
    status_code=status.HTTP_200_OK
)
def get_branches(
    current_user=Depends(get_current_user)
):
    return branch_manager_service.get_all_branches()

@router.get("/branch-performance")
def get_branch_performance(
    current_user=Depends(require_roles("BRANCH_MANAGER"))
):
    return branch_manager_service.get_branch_performance(current_user)


@router.get("/staff-metrics")
def get_staff_metrics(
    current_user=Depends(require_roles("BRANCH_MANAGER"))
):
    return branch_manager_service.get_staff_metrics(current_user)

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
        return branch_manager_service.create_branch(
            payload.model_dump()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

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
        return branch_manager_service.update_branch_manager(
            branch_code,
            payload.manager_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )