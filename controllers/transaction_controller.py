from fastapi import APIRouter, status, Query
from typing import List, Optional
from datetime import date

from models import schemas
from services.transaction_service import TransactionService


router = APIRouter()


# Process a money transfer between two existing bank accounts.
@router.post(
    "/transfer",
    response_model=schemas.TransactionResponse,
    status_code=status.HTTP_201_CREATED
)
def transfer_money(payload: schemas.TransferRequest):
    return TransactionService.transfer_money(payload)


# Retrieve transaction records, with optional filtering by date and transaction type.
@router.get(
    "",
    response_model=List[schemas.TransactionResponse],
    status_code=status.HTTP_200_OK
)
def get_transactions(
    start_date: Optional[date] = Query(default=None),
    type: Optional[str] = Query(default=None)
):
    return TransactionService.get_transactions(
        start_date=start_date,
        transaction_type=type
    )