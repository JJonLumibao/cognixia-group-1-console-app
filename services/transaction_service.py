import uuid
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import select
from models.database import SessionLocal, Transaction as TransactionORM, Account as AccountORM
from models.domain import TransactionType


def get_transactions(start_date=None, transaction_type=None) -> list:
    """Fetches transactions from the database, optionally filtering by date or type."""
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
                    raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

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


def create_transaction(txn_data: dict) -> dict:
    """Creates a new generic transaction and saves it to PostgreSQL."""
    t_type = TransactionType(txn_data.get("transaction_type"))

    new_id = str(uuid.uuid4())[:8]
    new_txn = TransactionORM(
        id=new_id,
        from_account_id=txn_data.get("from_account") or txn_data.get("from_account_id"),
        to_account_id=txn_data.get("to_account") or txn_data.get("to_account_id"),
        amount=float(txn_data.get("amount", 0)),
        type=t_type.value,
        timestamp=datetime.utcnow(),
    )

    with SessionLocal() as session:
        session.add(new_txn)
        session.commit()
        session.refresh(new_txn)

        return {
            "id": new_txn.id,
            "from_account_id": new_txn.from_account_id,
            "to_account_id": new_txn.to_account_id,
            "amount": new_txn.amount,
            "type": new_txn.type,
            "timestamp": new_txn.timestamp,
        }


def transfer_money(payload: dict) -> dict:
    """Handles moving funds between two accounts and recording the transaction in PostgreSQL."""
    from_account_id = payload.get("from_account_id")
    to_account_id = payload.get("to_account_id")
    amount = float(payload.get("amount", 0))

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Transfer amount must be greater than 0")
    if from_account_id == to_account_id:
        raise HTTPException(status_code=400, detail="Cannot transfer money to the same account")

    with SessionLocal() as session:
        from_account = session.get(AccountORM, from_account_id)
        if not from_account:
            raise HTTPException(status_code=404, detail="Sender account not found")

        to_account = session.get(AccountORM, to_account_id)
        if not to_account:
            raise HTTPException(status_code=404, detail="Recipient account not found")

        if from_account.active is False:
            raise HTTPException(status_code=400, detail="Sender account is inactive")
        if to_account.active is False:
            raise HTTPException(status_code=400, detail="Recipient account is inactive")
        if from_account.balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        from_account.balance -= amount
        to_account.balance += amount

        new_id = str(uuid.uuid4())[:8]
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
