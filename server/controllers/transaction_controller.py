from fastapi import APIRouter, status, HTTPException, Depends
from typing import List

from models import schemas
from services import transaction_service
from security.dependencies import require_roles

# Creates the router used for all transaction-related endpoints.
router = APIRouter()


# View transactions.
#
# Only tellers and administrators can view transaction records.
# The service layer handles retrieving the transactions from
# the database.
@router.get(
    "",
    response_model=List[schemas.TransactionResponse]
)
def get_transactions(
    current_user=Depends(require_roles("TELLER", "ADMIN", "BRANCH_MANAGER"))
):
    # Calls the transaction service to retrieve transaction records.
    return transaction_service.get_transactions()


@router.get(
    "/requests",
    response_model=List[schemas.TransactionRequestResponse],
    status_code=status.HTTP_200_OK
)
def list_transaction_requests(
    current_user=Depends(require_roles("TELLER", "BRANCH_MANAGER", "ADMIN"))
):
    return transaction_service.get_transaction_requests(current_user)


@router.post(
    "/requests",
    response_model=schemas.TransactionRequestResponse,
    status_code=status.HTTP_201_CREATED
)
def create_transaction_request(
    payload: schemas.TransactionRequestCreate,
    current_user=Depends(require_roles("CUSTOMER", "TELLER", "BRANCH_MANAGER", "ADMIN"))
):
    try:
        return transaction_service.create_transaction_request(
            payload.model_dump(),
            current_user
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/requests/{request_id}/approve",
    response_model=schemas.TransactionRequestResponse,
    status_code=status.HTTP_200_OK
)
def approve_transaction_request(
    request_id: str,
    current_user=Depends(require_roles("TELLER", "BRANCH_MANAGER", "ADMIN"))
):
    try:
        return transaction_service.approve_transaction_request(
            request_id,
            current_user
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/requests/{request_id}/reject",
    response_model=schemas.TransactionRequestResponse,
    status_code=status.HTTP_200_OK
)
def reject_transaction_request(
    request_id: str,
    current_user=Depends(require_roles("TELLER", "BRANCH_MANAGER", "ADMIN"))
):
    try:
        return transaction_service.reject_transaction_request(
            request_id,
            current_user
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Deposit money into a customer's account.
#
# Only tellers and administrators are allowed to perform deposits.
# The account ID and deposit amount are provided in the request body.
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
        # Convert the Pydantic request model into a dictionary
        # and pass it to the service layer along with the
        # authenticated user's information.
        return transaction_service.deposit_money(
            payload.model_dump(),
            current_user
        )

    # Converts a ValueError from the service layer into an
    # HTTP 400 Bad Request response.
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Withdraw money from a customer's account.
#
# Only tellers and administrators are allowed to perform withdrawals.
# The account ID and withdrawal amount are provided in the request body.
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
        # Convert the Pydantic request model into a dictionary
        # and pass it to the service layer along with the
        # authenticated user's information.
        return transaction_service.withdraw_money(
            payload.model_dump(),
            current_user
        )

    # Converts a ValueError from the service layer into an
    # HTTP 400 Bad Request response.
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Transfer money between accounts.
#
# Customers and administrators can initiate transfers.
# The service layer is responsible for checking whether the
# authenticated customer is allowed to use the accounts involved.
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
        # Convert the Pydantic request model into a dictionary
        # and pass it to the service layer along with the
        # authenticated user's information.
        return transaction_service.transfer_money(
            payload.model_dump(),
            current_user
        )

    # Converts a ValueError from the service layer into an
    # HTTP 400 Bad Request response.
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )