from fastapi import HTTPException
from datetime import date

from services.accounts import accounts
from services.transactions import transactions


class TransactionService:

    @staticmethod
    def transfer_money(payload):

        # Find the account sending the money.
        from_account = next(
            (
                account
                for account in accounts
                if account["id"] == payload.from_account_id
            ),
            None
        )

        if from_account is None:
            raise HTTPException(
                status_code=404,
                detail="Sender account not found"
            )

        # Find the account receiving the money.
        to_account = next(
            (
                account
                for account in accounts
                if account["id"] == payload.to_account_id
            ),
            None
        )

        if to_account is None:
            raise HTTPException(
                status_code=404,
                detail="Recipient account not found"
            )

        # The transfer amount must be greater than zero.
        if payload.amount <= 0:
            raise HTTPException(
                status_code=400,
                detail="Transfer amount must be greater than 0"
            )

        # Prevent transferring money to the same account.
        if payload.from_account_id == payload.to_account_id:
            raise HTTPException(
                status_code=400,
                detail="Cannot transfer money to the same account"
            )

        # Both accounts must be active.
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

        # The sender must have enough funds.
        if from_account["balance"] < payload.amount:
            raise HTTPException(
                status_code=400,
                detail="Insufficient funds"
            )

        # Transfer the money between the accounts.
        from_account["balance"] -= payload.amount
        to_account["balance"] += payload.amount

        # Create a transaction record.
        new_transaction = {
            "id": len(transactions) + 1,
            "from_account_id": payload.from_account_id,
            "to_account_id": payload.to_account_id,
            "amount": payload.amount,
            "type": "TRANSFER",
            "date": str(date.today())
        }

        # Store the transaction.
        transactions.append(new_transaction)

        return new_transaction

    @staticmethod
    def get_transactions(start_date=None, transaction_type=None):

        filtered_transactions = transactions

        # Filter transactions from the provided date onward.
        if start_date is not None:
            filtered_transactions = [
                transaction
                for transaction in filtered_transactions
                if transaction["date"] >= str(start_date)
            ]

        # Filter transactions by transaction type.
        if transaction_type is not None:
            filtered_transactions = [
                transaction
                for transaction in filtered_transactions
                if transaction["type"] == transaction_type
            ]

        return filtered_transactions