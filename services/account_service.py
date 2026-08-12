from fastapi import HTTPException
from sqlalchemy import select
from models.database import (
    SessionLocal,
    Account as AccountORM,
    Customer as CustomerORM,
    Branch as BranchORM,
    generate_id
)


class AccountService:

    # ACCOUNT CREATION
    # Create a new account for an existing customer.
    @staticmethod
    def create_account(payload, current_user=None):
        with SessionLocal() as session:

            # Verify that the customer who will own the account exists.
            customer = session.get(CustomerORM, payload.owner_id)

            if customer is None:
                raise HTTPException(
                    status_code=404,
                    detail="Customer not found"
                )

            # Verify that the branch assigned to the account exists.
            branch = session.get(BranchORM, payload.branch_id)

            if branch is None:
                raise HTTPException(
                    status_code=404,
                    detail="Branch not found"
                )

            # CUSTOMER authorization
            # Customers are only allowed to create accounts for themselves.
            if current_user and "CUSTOMER" in current_user.get("roles", []):
                user_email = current_user.get("email")

                # Find the customer record associated with the logged-in user's email.
                own_customer = session.execute(
                    select(CustomerORM).where(
                        CustomerORM.email == user_email
                    )
                ).scalar_one_or_none()

                if own_customer is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Customer profile not found"
                    )

                # Prevent a customer from creating an account for another customer.
                if own_customer.id != payload.owner_id:
                    raise HTTPException(
                        status_code=403,
                        detail="Customers may only create accounts for themselves"
                    )

            # Generate a unique ID for the new account.
            new_id = generate_id()

            # Create the account database record.
            new_account = AccountORM(
                id=new_id,
                owner_id=payload.owner_id,
                account_type=payload.account_type,
                balance=float(payload.balance),
                currency=str(payload.currency or "USD").upper(),
                branch_id=payload.branch_id,
                active=True,
            )

            # Save the new account to the database.
            session.add(new_account)
            session.commit()
            session.refresh(new_account)

            # Return the newly created account.
            return {
                "id": new_account.id,
                "owner_id": new_account.owner_id,
                "account_type": new_account.account_type,
                "balance": new_account.balance,
                "currency": new_account.currency,
                "branch_id": new_account.branch_id,
                "active": new_account.active,
            }


    # ACCOUNT RETRIEVAL
    # Retrieve accounts with optional branch and balance filters.
    @staticmethod
    def get_accounts(branch_id=None, min_balance=None, current_user=None):
        with SessionLocal() as session:

            # Start with a query that selects all accounts.
            stmt = select(AccountORM)

            # CUSTOMER authorization
            # Customers can only view accounts that they own.
            if "CUSTOMER" in current_user.get("roles", []):
                user_email = current_user.get("email")

                # Find the customer associated with the logged-in user's email.
                customer = session.execute(
                    select(CustomerORM).where(
                        CustomerORM.email == user_email
                    )
                ).scalar_one_or_none()

                if customer is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Customer profile not found"
                    )

                # Limit the query to accounts belonging to this customer.
                stmt = stmt.where(
                    AccountORM.owner_id == customer.id
                )

            # Optional branch filter.
            if branch_id is not None:
                stmt = stmt.where(
                    AccountORM.branch_id == str(branch_id)
                )

            # Optional minimum balance filter.
            if min_balance is not None:
                stmt = stmt.where(
                    AccountORM.balance >= float(min_balance)
                )

            # Execute the query and retrieve all matching accounts.
            results = session.scalars(stmt).all()

            # Convert database records into response dictionaries.
            return [
                {
                    "id": account.id,
                    "owner_id": account.owner_id,
                    "account_type": account.account_type,
                    "balance": account.balance,
                    "currency": account.currency,
                    "branch_id": account.branch_id,
                    "active": account.active,
                }
                for account in results
            ]


    # ACCOUNT STATUS
    # Activate or deactivate a specific bank account.
    @staticmethod
    def update_account_status(account_id, payload, current_user):
        with SessionLocal() as session:

            # Find the account being updated.
            account = session.get(AccountORM, account_id)

            if not account:
                raise HTTPException(
                    status_code=404,
                    detail="Account not found"
                )

            # Get the roles stored in the authenticated user's JWT.
            roles = current_user.get("roles", [])

            # ADMIN authorization
            # Administrators can activate or deactivate any account.
            if "ADMIN" in roles:
                account.active = payload.active

            # CUSTOMER authorization
            # Customers can only change the status of their own accounts.
            elif "CUSTOMER" in roles:

                user_email = current_user.get("email")

                # Find the customer associated with the logged-in user's email.
                customer = session.execute(
                    select(CustomerORM).where(
                        CustomerORM.email == user_email
                    )
                ).scalar_one_or_none()

                if customer is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Customer profile not found"
                    )

                # IMPORTANT:
                # Account.owner_id refers to Customer.id,
                # NOT User.id from the JWT.
                if account.owner_id != customer.id:
                    raise HTTPException(
                        status_code=403,
                        detail="You are not authorized to modify this account"
                    )

                # Update the account's active status.
                account.active = payload.active

            # Reject any role that is not authorized to modify account status.
            else:
                raise HTTPException(
                    status_code=403,
                    detail="You are not authorized to modify this account"
                )

            # Save the status change to the database.
            session.commit()
            session.refresh(account)

            # Return the updated account.
            return {
                "id": account.id,
                "owner_id": account.owner_id,
                "account_type": account.account_type,
                "balance": account.balance,
                "currency": account.currency,
                "branch_id": account.branch_id,
                "active": account.active,
            }