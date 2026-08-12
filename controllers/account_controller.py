from fastapi import APIRouter, status, Depends, Query
from typing import List, Optional

from models import schemas
from services.account_service import AccountService
from security.dependencies import require_roles

# Creates the router used for all account-related API endpoints.
router = APIRouter()


# Creates a new bank account for an existing customer.
# Only customers and admins are allowed to create accounts.
@router.post(
    "",
    response_model=schemas.AccountResponse,
    status_code=status.HTTP_201_CREATED
)
def create_account(
    payload: schemas.AccountCreate,
    current_user=Depends(require_roles("CUSTOMER", "ADMIN"))
):
    # Passes the account information and authenticated user
    # to the service layer where the account is created.
    return AccountService.create_account(payload, current_user)


# Retrieves accounts from the database.
# Optional query parameters allow filtering by branch and minimum balance.
#
# Example:
# GET /accounts?branch_id=BR001
# GET /accounts?min_balance=500
# GET /accounts?branch_id=BR001&min_balance=500
#
# Customers are restricted to seeing their own accounts.
# Admins can retrieve accounts across the system.
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
    # Sends the optional filters and authenticated user
    # to the service layer to retrieve the appropriate accounts.
    return AccountService.get_accounts(
        branch_id=branch_id,
        min_balance=min_balance,
        current_user=current_user
    )


# Updates the active/inactive status of a specific account.
#
# The account ID is provided in the URL, while the new active
# status is provided in the request body.
#
# Customers can only modify accounts that belong to them.
# Admins can modify any account.
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
    # Sends the account ID, requested status change, and
    # authenticated user to the service layer.
    return AccountService.update_account_status(
        account_id,
        payload,
        current_user
    )