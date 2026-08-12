from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select

from models.database import (
    SessionLocal,
    Transaction as TransactionORM,
    Account as AccountORM,
    Customer as CustomerORM,
    generate_id,
)
from models.domain import TransactionType


# Retrieve transactions, with optional filtering by date or transaction type.
def get_transactions(start_date=None, transaction_type=None) -> list:

    with SessionLocal() as session:
        stmt = select(TransactionORM)

        # Filter transactions by their transaction type when provided.
        if transaction_type:
            stmt = stmt.where(TransactionORM.type == transaction_type)

        # Filter transactions to only those occurring on or after the provided date.
        if start_date:
            if isinstance(start_date, str):
                try:
                    dt = datetime.strptime(start_date, "%Y-%m-%d")
                    stmt = stmt.where(TransactionORM.timestamp >= dt)

                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid date format. Use YYYY-MM-DD."
                    )

        transactions = session.scalars(stmt).all()

        # Convert database transaction objects into response dictionaries.
        return [
            {
                "id": txn.id,
                "from_account_id": txn.from_account_id,
                "to_account_id": txn.to_account_id,
                "amount": txn.amount,
                "type": txn.type,
                "timestamp": txn.timestamp,
            }
            for txn in transactions
        ]


# Deposit money into an existing customer's account.
def deposit_money(payload: dict, current_user: dict) -> dict:

    account_id = payload.get("account_id")
    amount = float(payload.get("amount", 0))

    # Deposits must be greater than zero.
    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Deposit amount must be greater than 0"
        )

    with SessionLocal() as session:
        # Find the account receiving the deposit.
        account = session.get(AccountORM, account_id)

        if not account:
            raise HTTPException(
                status_code=404,
                detail="Account not found"
            )

        # Prevent transactions against inactive accounts.
        if account.active is False:
            raise HTTPException(
                status_code=400,
                detail="Account is inactive"
            )

        # Staff members cannot interact with accounts outside their assigned branch.
        if current_user.get("branch_id") is not None and current_user.get("branch_id") != account.branch_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot interact with an account outside your branch"
            )

        # Add the deposited amount to the account balance.
        account.balance += amount

        # Create a transaction record for the deposit.
        transaction = TransactionORM(
            id=generate_id(),
            from_account_id=None,
            to_account_id=account_id,
            amount=amount,
            type=TransactionType.DEPOSIT.value,
            timestamp=datetime.utcnow()
        )

        session.add(transaction)
        session.commit()
        session.refresh(transaction)

        # Return the newly created transaction.
        return {
            "id": transaction.id,
            "from_account_id": transaction.from_account_id,
            "to_account_id": transaction.to_account_id,
            "amount": transaction.amount,
            "type": transaction.type,
            "timestamp": transaction.timestamp,
        }


# Withdraw money from an existing customer's account.
def withdraw_money(payload: dict, current_user: dict) -> dict:

    account_id = payload.get("account_id")
    amount = float(payload.get("amount", 0))

    # Withdrawals must be greater than zero.
    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Withdrawal amount must be greater than 0"
        )

    with SessionLocal() as session:
        # Find the account being used for the withdrawal.
        account = session.get(AccountORM, account_id)

        if not account:
            raise HTTPException(
                status_code=404,
                detail="Account not found"
            )

        # Prevent transactions against inactive accounts.
        if account.active is False:
            raise HTTPException(
                status_code=400,
                detail="Account is inactive"
            )

        # Staff members cannot interact with accounts outside their assigned branch.
        if current_user.get("branch_id") is not None and current_user.get("branch_id") != account.branch_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot interact with an account outside your branch"
            )

        # Make sure the account has enough funds for the withdrawal.
        if account.balance < amount:
            raise HTTPException(
                status_code=400,
                detail="Insufficient funds"
            )

        # Subtract the withdrawal amount from the account balance.
        account.balance -= amount

        # Create a transaction record for the withdrawal.
        transaction = TransactionORM(
            id=generate_id(),
            from_account_id=account_id,
            to_account_id=None,
            amount=amount,
            type=TransactionType.WITHDRAWAL.value,
            timestamp=datetime.utcnow()
        )

        session.add(transaction)
        session.commit()
        session.refresh(transaction)

        # Return the newly created transaction.
        return {
            "id": transaction.id,
            "from_account_id": transaction.from_account_id,
            "to_account_id": transaction.to_account_id,
            "amount": transaction.amount,
            "type": transaction.type,
            "timestamp": transaction.timestamp,
        }


# Transfer money from one account to another.
def transfer_money(payload: dict, current_user: dict) -> dict:

    from_account_id = payload.get("from_account_id")
    to_account_id = payload.get("to_account_id")
    amount = float(payload.get("amount", 0))

    # Transfers must be greater than zero.
    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Transfer amount must be greater than 0"
        )

    # Prevent transferring money from an account back into itself.
    if from_account_id == to_account_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot transfer money to the same account"
        )

    with SessionLocal() as session:
        # Retrieve the account sending the money.
        from_account = session.get(AccountORM, from_account_id)

        if not from_account:
            raise HTTPException(
                status_code=404,
                detail="Sender account not found"
            )

        # Staff members cannot transfer from accounts outside their assigned branch.
        if current_user.get("branch_id") is not None and current_user.get("branch_id") != from_account.branch_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot transfer from an account outside your branch"
            )

        # CUSTOMER can only transfer from their own account.
        if "CUSTOMER" in current_user.get("roles", []):
            user_email = current_user.get("email")

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

            # Account.owner_id refers to Customer.id, not User.id.
            if from_account.owner_id != customer.id:
                raise HTTPException(
                    status_code=403,
                    detail="You can only transfer from your own account"
                )

        # Retrieve the account receiving the money.
        to_account = session.get(AccountORM, to_account_id)

        if not to_account:
            raise HTTPException(
                status_code=404,
                detail="Recipient account not found"
            )

        # Both accounts must be active before a transfer can occur.
        if from_account.active is False:
            raise HTTPException(
                status_code=400,
                detail="Sender account is inactive"
            )

        if to_account.active is False:
            raise HTTPException(
                status_code=400,
                detail="Recipient account is inactive"
            )

        # Make sure the sender has enough funds.
        if from_account.balance < amount:
            raise HTTPException(
                status_code=400,
                detail="Insufficient funds"
            )

        # Move the money between the two account balances.
        from_account.balance -= amount
        to_account.balance += amount

        # Generate a unique ID for the transfer transaction.
        new_id = generate_id()

        # Create a record documenting the transfer.
        transaction_record = TransactionORM(
            id=new_id,
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=amount,
            type=TransactionType.TRANSFER.value,
            timestamp=datetime.utcnow(),
        )

        session.add(transaction_record)
        session.commit()
        session.refresh(transaction_record)

        # Return the completed transfer transaction.
        return {
            "id": transaction_record.id,
            "from_account_id": transaction_record.from_account_id,
            "to_account_id": transaction_record.to_account_id,
            "amount": transaction_record.amount,
            "type": transaction_record.type,
            "timestamp": transaction_record.timestamp,
        }