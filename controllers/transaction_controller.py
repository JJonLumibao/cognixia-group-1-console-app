from fastapi import APIRouter, HTTPException
from services.accounts import accounts
from services.transactions import transactions
from datetime import date

router = APIRouter()


@router.post("/transfer", status_code=201)
def transfer_money(transfer: dict):
    from_account_id = transfer.get("from_account_id")
    to_account_id = transfer.get("to_account_id")
    amount = transfer.get("amount")

    # Make sure the transfer amount is provided and is greater than zero.
    # Transfers with zero or negative amounts are not valid.
    if amount is None or amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Transfer amount must be greater than 0"
        )

    # Find the account that will send the money using the provided account ID.
    from_account = next(
        (account for account in accounts
         if account["id"] == from_account_id),
        None
    )

    # Stop the transfer if the sender's account does not exist.
    if from_account is None:
        raise HTTPException(
            status_code=404,
            detail="Sender account not found"
        )

    # Find the account that will receive the money using the provided account ID.
    to_account = next(
        (account for account in accounts
         if account["id"] == to_account_id),
        None
    )

    # Stop the transfer if the recipient's account does not exist.
    if to_account is None:
        raise HTTPException(
            status_code=404,
            detail="Recipient account not found"
        )

    # Prevent a transfer from being made to the same account.
    if from_account_id == to_account_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot transfer money to the same account"
        )

    # Only active accounts are allowed to send or receive transfers.
    if not from_account["active"]:
        raise HTTPException(
            status_code=400,
            detail="Sender account is inactive"
        )

    if not to_account["active"]:
        raise HTTPException(
            status_code=400,
            detail="Recipient account is inactive"
        )

    # Make sure the sender has enough funds to complete the transfer.
    if from_account["balance"] < amount:
        raise HTTPException(
            status_code=400,
            detail="Insufficient funds"
        )

    # Update both account balances to complete the transfer.
    # The sender's balance is reduced while the recipient's balance increases.
    from_account["balance"] -= amount
    to_account["balance"] += amount

    # Create a record of the completed transfer with the account IDs,
    # transfer amount, transaction type, and current date.
    new_transaction = {
        "id": len(transactions) + 1,
        "from_account_id": from_account_id,
        "to_account_id": to_account_id,
        "amount": amount,
        "type": "TRANSFER",
        "date": str(date.today())
    }

    # Store the transaction in the in-memory transaction data.
    transactions.append(new_transaction)

    # Return the completed transaction to the client.
    return new_transaction