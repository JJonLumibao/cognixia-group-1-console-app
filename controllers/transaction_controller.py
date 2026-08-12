from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from models import schemas
from services import transaction_service # Adjust this import if your file is named differently
from security.dependencies import require_roles

router = APIRouter()

# TELLER / ADMIN
# View transactions
@router.get("", response_model=List[schemas.TransactionResponse])
def get_transactions(current_user=Depends(require_roles("TELLER", "ADMIN"))):
    return transaction_service.get_transactions()

# TELLER / ADMIN
# Deposit money into a customer's account
@router.post(
    "/deposit",
    response_model=schemas.TransactionResponse,
    status_code=status.HTTP_201_CREATED
)
def deposit(
    payload: schemas.DepositRequest,
    current_user=Depends(require_roles("TELLER", "ADMIN"))
):
    try:
        return transaction_service.deposit_money(payload.model_dump())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# TELLER / ADMIN
# Withdraw money from a customer's account
@router.post(
    "/withdraw",
    response_model=schemas.TransactionResponse,
    status_code=status.HTTP_201_CREATED
)
def withdraw(
    payload: schemas.WithdrawRequest,
    current_user=Depends(require_roles("TELLER", "ADMIN"))
):
    try:
        return transaction_service.withdraw_money(payload.model_dump())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# CUSTOMER / ADMIN
# Transfer money between accounts
@router.post(
    "/transfer",
    response_model=schemas.TransactionResponse,
    status_code=status.HTTP_201_CREATED
)
def transfer_funds(
    payload: schemas.TransferCreate,
    current_user=Depends(
        require_roles("CUSTOMER", "ADMIN")
    )
):
    try:
        return transaction_service.transfer_money(
            payload.model_dump(),
            current_user
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )