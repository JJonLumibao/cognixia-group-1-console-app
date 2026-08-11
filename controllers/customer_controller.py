from fastapi import APIRouter, status, Query
from typing import List, Optional
from app.models import schemas
from services import customers


router = APIRouter(prefix="/customers", tags=["Customers"])
@router.post("", response_model=schemas.CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(payload: schemas.CustomerCreate):
   return customers.create_customer(payload)


@router.get("", response_model=List[schemas.CustomerResponse])
def get_customers():
   return customers.get_all_customers()


@router.get("/{customer_id}", response_model=schemas.CustomerResponse)
def get_customer(customer_id: int):
   return customers.get_customer_by_id(customer_id)


@router.put("/{customer_id}", response_model=schemas.CustomerResponse)
def update_customer(customer_id: int, payload: schemas.CustomerUpdate):
   return customers.update_customer(customer_id, payload)


@router.delete("/{customer_id}", response_model=schemas.CustomerResponse)
def deactivate_customer(customer_id: int):
   return customers.deactivate_customer(customer_id)
