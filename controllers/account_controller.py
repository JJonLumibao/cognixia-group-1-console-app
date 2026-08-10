from fastapi import APIRouter, HTTPException
from services.accounts import accounts
from services.customers import customers

router = APIRouter()


@router.post("/", status_code=201)
def create_account(account: dict):
    customer_id = account.get("customer_id")

    # Verify that the customer requesting the account exists
    # before creating an account associated with their customer ID.
    customer = next(
        (customer for customer in customers if customer["id"] == customer_id),
        None
    )

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    # Generate a unique account ID by using the current highest ID
    # and incrementing it by one.
    new_id = max(account["id"] for account in accounts) + 1

    # Build the new account using the provided information.
    # New accounts are active by default and start with a balance
    # of 0.00 if no initial balance is provided.
    new_account = {
        "id": new_id,
        "customer_id": customer_id,
        "account_type": account.get("account_type"),
        "balance": account.get("balance", 0.00),
        "branch_id": account.get("branch_id"),
        "active": True
    }

    # Add the newly created account to the in-memory account data
    # so it can be accessed by other API operations.
    accounts.append(new_account)

    # Return the newly created account to the client.
    return new_account