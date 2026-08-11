from uuid import uuid4
from datetime import datetime

from models.database import Base, SessionLocal, engine, Customer, Account, Transaction
from models.domain import TransactionType


def _new_id() -> str:
    return str(uuid4())[:8]


def seed_database() -> None:
    """Create tables if needed and insert initial sample data."""
    Base.metadata.create_all(bind=engine)

    customer_1 = Customer(
        id="cust001",
        name="Alice Johnson",
        email="alice.johnson@example.com",
        branch_id="BR001",
        active=True,
    )
    customer_2 = Customer(
        id="cust002",
        name="Bob Martinez",
        email="bob.martinez@example.com",
        branch_id="BR002",
        active=True,
    )

    account_1 = Account(
        id="acct001",
        owner_id=customer_1.id,
        account_type="savings",
        balance=1200.50,
        branch_id=customer_1.branch_id,
        active=True,
    )
    account_2 = Account(
        id="acct002",
        owner_id=customer_1.id,
        account_type="checking",
        balance=450.00,
        branch_id=customer_1.branch_id,
        active=True,
    )
    account_3 = Account(
        id="acct003",
        owner_id=customer_2.id,
        account_type="checking",
        balance=780.30,
        branch_id=customer_2.branch_id,
        active=True,
    )

    transaction_1 = Transaction(
        id="txn001",
        from_account_id=account_1.id,
        to_account_id=account_2.id,
        amount=150.0,
        type=TransactionType.TRANSFER.value,
        timestamp=datetime.utcnow(),
    )
    transaction_2 = Transaction(
        id="txn002",
        from_account_id=account_3.id,
        to_account_id=account_1.id,
        amount=75.25,
        type=TransactionType.TRANSFER.value,
        timestamp=datetime.utcnow(),
    )

    with SessionLocal() as session:
        session.merge(customer_1)
        session.merge(customer_2)
        session.merge(account_1)
        session.merge(account_2)
        session.merge(account_3)
        session.commit()

    with SessionLocal() as session:
        session.merge(transaction_1)
        session.merge(transaction_2)
        session.commit()

    print("Seed data inserted successfully.")


if __name__ == "__main__":
    seed_database()
