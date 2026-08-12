from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from security.dependencies import get_current_user
from models import schemas
from services import customer_service

router = APIRouter()

@router.post("", response_model=schemas.CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(payload: schemas.CustomerCreate):
    # .model_dump() converts the Pydantic schema into a dictionary for the service layer
    return customer_service.create_customer(payload.model_dump())

@router.get("", response_model=List[schemas.CustomerResponse])
def get_customers():
    return customer_service.get_all_customers()

@router.get(
    "/me",
    response_model=schemas.CustomerResponse
)
def get_my_customer(
    current_user=Depends(get_current_user)
):

    try:
        return customer_service.get_customer_by_email(
            current_user["email"]
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/{customer_id}", response_model=schemas.CustomerResponse)
def get_customer(customer_id: str):
    try:
        return customer_service.get_customers_by_id(customer_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.put("/{customer_id}", response_model=schemas.CustomerResponse)
def update_customer(customer_id: str, payload: schemas.CustomerUpdate):
    try:
        # exclude_unset=True ensures we only pass fields the user actually wants to update
        updated_data = payload.model_dump(exclude_unset=True)
        return customer_service.update_customer(customer_id, updated_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/{customer_id}", response_model=schemas.CustomerResponse)
def deactivate_customer(customer_id: str):
    try:
        return customer_service.deactivate_customer(customer_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
