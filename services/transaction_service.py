from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select

from models.database import (
    SessionLocal,
    Transaction as TransactionORM,
    Account as AccountORM,
    generate_id,
)
from models.domain import TransactionType


def get_transactions(start_date=None, transaction_type=None) -> list:
    """Fetch transactions, optionally filtered by date or type."""

    with SessionLocal() as session:
        stmt = select(TransactionORM)

        if transaction_type:
            stmt = stmt.where(TransactionORM.type == transaction_type)

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


def deposit_money(payload: dict, current_user: dict) -> dict:
    """Deposits money into a customer's account."""

    account_id = payload.get("account_id")
    amount = float(payload.get("amount", 0))

    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Deposit amount must be greater than 0"
        )

    with SessionLocal() as session:
        account = session.get(AccountORM, account_id)

        if not account:
            raise HTTPException(
                status_code=404,
                detail="Account not found"
            )

        if account.active is False:
            raise HTTPException(
                status_code=400,
                detail="Account is inactive"
            )

        if current_user.get("branch_id") is not None and current_user.get("branch_id") != account.branch_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot interact with an account outside your branch"
            )

        account.balance += amount

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

        return {
            "id": transaction.id,
            "from_account_id": transaction.from_account_id,
            "to_account_id": transaction.to_account_id,
            "amount": transaction.amount,
            "type": transaction.type,
            "timestamp": transaction.timestamp,
        }


def withdraw_money(payload: dict, current_user: dict) -> dict:
    """Withdraws money from a customer's account."""

    account_id = payload.get("account_id")
    amount = float(payload.get("amount", 0))

    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Withdrawal amount must be greater than 0"
        )

    with SessionLocal() as session:
        account = session.get(AccountORM, account_id)

        if not account:
            raise HTTPException(
                status_code=404,
                detail="Account not found"
            )

        if account.active is False:
            raise HTTPException(
                status_code=400,
                detail="Account is inactive"
            )

        if current_user.get("branch_id") is not None and current_user.get("branch_id") != account.branch_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot interact with an account outside your branch"
            )

        if account.balance < amount:
            raise HTTPException(
                status_code=400,
                detail="Insufficient funds"
            )

        account.balance -= amount

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

        return {
            "id": transaction.id,
            "from_account_id": transaction.from_account_id,
            "to_account_id": transaction.to_account_id,
            "amount": transaction.amount,
            "type": transaction.type,
            "timestamp": transaction.timestamp,
        }


def transfer_money(payload: dict, current_user: dict) -> dict:
    """Handles moving funds between two accounts and recording the transaction."""

    from_account_id = payload.get("from_account_id")
    to_account_id = payload.get("to_account_id")
    amount = float(payload.get("amount", 0))

    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Transfer amount must be greater than 0"
        )

    if from_account_id == to_account_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot transfer money to the same account"
        )

    with SessionLocal() as session:
        from_account = session.get(AccountORM, from_account_id)

        if not from_account:
            raise HTTPException(
                status_code=404,
                detail="Sender account not found"
            )

        if current_user.get("branch_id") is not None and current_user.get("branch_id") != from_account.branch_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot transfer from an account outside your branch"
            )

        # CUSTOMER can only transfer from their own account
        if "CUSTOMER" in current_user.get("roles", []):
            user_id = current_user.get("sub")

            if from_account.owner_id != user_id:
                raise HTTPException(
                    status_code=403,
                    detail="You can only transfer from your own account"
                )

        to_account = session.get(AccountORM, to_account_id)

        if not to_account:
            raise HTTPException(
                status_code=404,
                detail="Recipient account not found"
            )

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

        if from_account.balance < amount:
            raise HTTPException(
                status_code=400,
                detail="Insufficient funds"
            )

        from_account.balance -= amount
        to_account.balance += amount

        new_id = generate_id()

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

        return {
            "id": transaction_record.id,
            "from_account_id": transaction_record.from_account_id,
            "to_account_id": transaction_record.to_account_id,
            "amount": transaction_record.amount,
            "type": transaction_record.type,
            "timestamp": transaction_record.timestamp,
        }