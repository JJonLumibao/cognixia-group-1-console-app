from fastapi import APIRouter, status, Depends, Query
from typing import List, Optional

from models import schemas
from services.account_service import AccountService
from security.dependencies import require_roles

router = APIRouter()


# Create a new bank account for an existing customer.
@router.post(
    "",
    response_model=schemas.AccountResponse,
    status_code=status.HTTP_201_CREATED
)
def create_account(
    payload: schemas.AccountCreate,
    current_user=Depends(require_roles("CUSTOMER", "ADMIN"))
):
    return AccountService.create_account(payload, current_user)


# Retrieve all accounts, with optional filtering by branch and minimum balance.
@router.get(
    "",
    response_model=List[schemas.AccountResponse],
    status_code=status.HTTP_200_OK
)
def get_accounts(
    branch_id: Optional[str] = Query(default=None),
    min_balance: Optional[float] = Query(default=None),
    current_user=Depends(require_roles("CUSTOMER", "ADMIN"))
):
    return AccountService.get_accounts(
        branch_id=branch_id,
        min_balance=min_balance,
        current_user=current_user
    )

@router.patch(
    "/{account_id}/status",
    response_model=schemas.AccountResponse,
    status_code=status.HTTP_200_OK
)
def update_account_status(
    account_id: str,
    payload: schemas.AccountStatusUpdate,
    current_user=Depends(require_roles("CUSTOMER", "ADMIN"))
):
    return AccountService.update_account_status(
        account_id,
        payload,
        current_user
    )