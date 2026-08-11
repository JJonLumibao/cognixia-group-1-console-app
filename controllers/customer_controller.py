from fastapi import APIRouter, status, HTTPException
from typing import List
from models import schemas
from services import customers 

router = APIRouter()

@router.post("", response_model=schemas.CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(payload: schemas.CustomerCreate):
    # .model_dump() converts the Pydantic schema into a dictionary for the service layer
    return customers.create_customer(payload.model_dump())

@router.get("", response_model=List[schemas.CustomerResponse])
def get_customers():
    return customers.get_all_customers()

@router.get("/{customer_id}", response_model=schemas.CustomerResponse)
def get_customer(customer_id: str):
    try:
        # Adjusted to match the exact function name in your service layer
        return customers.get_customers_by_id(customer_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.put("/{customer_id}", response_model=schemas.CustomerResponse)
def update_customer(customer_id: str, payload: schemas.CustomerUpdate):
    try:
        # exclude_unset=True ensures we only pass fields the user actually wants to update
        updated_data = payload.model_dump(exclude_unset=True)
        return customers.update_customer(customer_id, updated_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{customer_id}", response_model=schemas.CustomerResponse)
def deactivate_customer(customer_id: str):
    try:
        return customers.deactivate_customer(customer_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))