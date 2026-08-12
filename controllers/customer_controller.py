from fastapi import APIRouter, Depends, status, HTTPException
from typing import List

from security.dependencies import get_current_user
from models import schemas
from services import customer_service

# Creates the router used for customer-related endpoints.
router = APIRouter()


# Creates a new customer.
@router.post(
    "",
    response_model=schemas.CustomerResponse,
    status_code=status.HTTP_201_CREATED
)
def create_customer(payload: schemas.CustomerCreate):

    # .model_dump() converts the Pydantic schema into a dictionary
    # that can be passed to the service layer.
    return customer_service.create_customer(payload.model_dump())


# Retrieves all customers.
@router.get(
    "",
    response_model=List[schemas.CustomerResponse]
)
def get_customers():

    # Calls the service layer to retrieve all customers.
    return customer_service.get_all_customers()


# Retrieves the customer profile associated with the
# currently authenticated user.
#
# The user's email is taken from the authentication token
# rather than being supplied manually in the URL.
@router.get(
    "/me",
    response_model=schemas.CustomerResponse
)
def get_my_customer(
    current_user=Depends(get_current_user)
):

    try:
        # Uses the authenticated user's email to find
        # the corresponding customer record.
        return customer_service.get_customer_by_email(
            current_user["email"]
        )

    # Converts a missing customer into an HTTP 404 response.
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# Retrieves a specific customer using their customer ID.
@router.get(
    "/{customer_id}",
    response_model=schemas.CustomerResponse
)
def get_customer(customer_id: str):

    try:
        # Passes the customer ID to the service layer.
        return customer_service.get_customers_by_id(customer_id)

    # Returns 404 when the requested customer does not exist.
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# Updates an existing customer's information.
@router.put(
    "/{customer_id}",
    response_model=schemas.CustomerResponse
)
def update_customer(
    customer_id: str,
    payload: schemas.CustomerUpdate
):

    try:
        # exclude_unset=True ensures that only fields actually
        # included by the client are passed to the service.
        #
        # This prevents unspecified fields from being overwritten.
        updated_data = payload.model_dump(exclude_unset=True)

        # Sends the customer ID and requested changes
        # to the service layer.
        return customer_service.update_customer(
            customer_id,
            updated_data
        )

    # Returns 404 if the customer cannot be found.
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# Deactivates an existing customer.
#
# The customer record is not necessarily deleted from the database;
# instead, the service can mark the customer as inactive.
@router.delete(
    "/{customer_id}",
    response_model=schemas.CustomerResponse
)
def deactivate_customer(customer_id: str):

    try:
        # Sends the customer ID to the service layer.
        return customer_service.deactivate_customer(customer_id)

    # Returns 404 if the customer does not exist.
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )