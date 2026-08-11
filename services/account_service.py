from fastapi import HTTPException

from services.accounts import accounts
from services.customers import customers


class AccountService:

    @staticmethod
    def create_account(payload):

        # Verify that the customer exists before creating the account.
        customer = next(
            (
                customer
                for customer in customers
                if customer["id"] == payload.customer_id
            ),
            None
        )

        if customer is None:
            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )

        # Generate a new account ID.
        new_id = max(account["id"] for account in accounts) + 1

        # Create the new account.
        new_account = {
            "id": new_id,
            "customer_id": payload.customer_id,
            "account_type": payload.account_type,
            "balance": payload.balance,
            "branch_id": payload.branch_id,
            "active": True
        }

        # Store the account in the in-memory data.
        accounts.append(new_account)

        return new_account

    @staticmethod
    def get_accounts(branch_id=None, min_balance=None):

        # Start with all accounts.
        filtered_accounts = accounts

        # Filter accounts by branch when branch_id is provided.
        if branch_id is not None:
            filtered_accounts = [
                account
                for account in filtered_accounts
                if account["branch_id"] == branch_id
            ]

        # Filter accounts by minimum balance when provided.
        if min_balance is not None:
            filtered_accounts = [
                account
                for account in filtered_accounts
                if account["balance"] >= min_balance
            ]

        return filtered_accounts