from fastapi import APIRouter, status, HTTPException
from typing import List
from models import schemas
from services import transaction_service # Adjust this import if your file is named differently

router = APIRouter()

@router.post("", response_model=schemas.TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(payload: schemas.TransactionCreate):
    try:
        # .model_dump() converts Pydantic schema to dict
        return transaction_service.create_transaction(payload.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("", response_model=List[schemas.TransactionResponse])
def get_transactions():
    return transaction_service.get_transactions()

@router.post("/transfer", response_model=schemas.TransactionResponse, status_code=status.HTTP_201_CREATED)
def transfer_funds(payload: schemas.TransferCreate):
    try:
        # Calls the specific transfer_money function we built in the service layer
        return transaction_service.transfer_money(payload.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))