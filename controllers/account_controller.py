from fastapi import APIRouter, status, Query
from typing import List, Optional

from models import schemas
from services.account_service import AccountService


router = APIRouter()


# Create a new bank account for an existing customer.
@router.post(
    "",
    response_model=schemas.AccountResponse,
    status_code=status.HTTP_201_CREATED
)
def create_account(payload: schemas.AccountCreate):
    return AccountService.create_account(payload)


# Retrieve all accounts, with optional filtering by branch and minimum balance.
@router.get(
    "",
    response_model=List[schemas.AccountResponse],
    status_code=status.HTTP_200_OK
)
def get_accounts(
    branch_id: Optional[int] = Query(default=None),
    min_balance: Optional[float] = Query(default=None)
):
    return AccountService.get_accounts(
        branch_id=branch_id,
        min_balance=min_balance
    )