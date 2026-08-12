import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_db.sqlite")
os.environ.setdefault("JWT_SECRET", "testsecret")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from main import app
from models.database import Base, engine, SessionLocal, User, Customer, Account
from security.security import create_access_token, hash_password

client = TestClient(app)


def setup_module(module):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        user = User(
            id="user12345678",
            email="teller@example.com",
            password_hash=hash_password("secret123"),
            role="TELLER",
            branch_id="BR001",
            active=True,
        )
        customer = Customer(
            id="cust12345678",
            name="Test Customer",
            email="customer@example.com",
            branch_id="BR001",
            active=True,
        )
        customer2 = Customer(
            id="cust87654321",
            name="Other Branch Customer",
            email="other@example.com",
            branch_id="BR002",
            active=True,
        )
        account = Account(
            id="acct12345678",
            owner_id=customer.id,
            account_type="checking",
            balance=1000.0,
            branch_id="BR001",
            active=True,
        )
        other_account = Account(
            id="acct87654321",
            owner_id=customer2.id,
            account_type="checking",
            balance=500.0,
            branch_id="BR002",
            active=True,
        )
        session.add_all([user, customer, customer2, account, other_account])
        session.commit()


def test_deposit_outside_branch_forbidden():
    token = create_access_token(
        user_id="user12345678",
        email="teller@example.com",
        role="TELLER",
        branch_id="BR001"
    )

    response = client.post(
        "/api/v1/transactions/deposit",
        headers={"Authorization": f"Bearer {token}"},
        json={"account_id": "acct87654321", "amount": 100.0},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Cannot interact with an account outside your branch"


def test_withdraw_inactive_account_forbidden():
    token = create_access_token(
        user_id="user12345678",
        email="teller@example.com",
        role="TELLER",
        branch_id="BR001"
    )

    with SessionLocal() as session:
        account = session.get(Account, "acct12345678")
        account.active = False
        session.commit()

    response = client.post(
        "/api/v1/transactions/withdraw",
        headers={"Authorization": f"Bearer {token}"},
        json={"account_id": "acct12345678", "amount": 50.0},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Account is inactive"


def test_transfer_same_account_invalid():
    token = create_access_token(
        user_id="admin12345678",
        email="admin@example.com",
        role="ADMIN",
        branch_id="BR001"
    )

    response = client.post(
        "/api/v1/transactions/transfer",
        headers={"Authorization": f"Bearer {token}"},
        json={"from_account_id": "acct12345678", "to_account_id": "acct12345678", "amount": 10.0},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot transfer money to the same account"


def test_deactivate_customer_cascades_account():
    with SessionLocal() as session:
        customer = session.get(Customer, "cust12345678")
        assert customer.active is True
        for account in customer.accounts:
            assert account.active is False or account.active is True

    # deactivate by direct service call to avoid endpoint auth complexity
    from services.customer_service import deactivate_customer

    result = deactivate_customer("cust12345678")
    assert result["active"] is False
    with SessionLocal() as session:
        accounts = session.scalars(
            select(Account).where(Account.owner_id == "cust12345678")
        ).all()
        assert all(account.active is False for account in accounts)


def test_transfer_outside_branch_forbidden():
    token = create_access_token(
        user_id="admin12345678",
        email="admin@example.com",
        role="ADMIN",
        branch_id="BR001"
    )

    response = client.post(
        "/api/v1/transactions/transfer",
        headers={"Authorization": f"Bearer {token}"},
        json={"from_account_id": "acct87654321", "to_account_id": "acct12345678", "amount": 10.0},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Cannot transfer from an account outside your branch"


def test_transfer_between_different_currencies_converts_amount():
    token = create_access_token(
        user_id="admin12345678",
        email="admin@example.com",
        role="ADMIN",
        branch_id="BR001"
    )

    with SessionLocal() as session:
        sender = session.get(Account, "acct12345678")
        recipient = session.get(Account, "acct87654321")
        sender.currency = "USD"
        recipient.currency = "EUR"
        sender.balance = 1000.0
        recipient.balance = 500.0
        session.commit()

    response = client.post(
        "/api/v1/transactions/transfer",
        headers={"Authorization": f"Bearer {token}"},
        json={"from_account_id": "acct12345678", "to_account_id": "acct87654321", "amount": 100.0},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["amount"] == 100.0
    assert payload["currency"] == "USD"
    assert payload["converted_amount"] == 92.0
    assert payload["converted_currency"] == "EUR"

    with SessionLocal() as session:
        sender = session.get(Account, "acct12345678")
        recipient = session.get(Account, "acct87654321")
        assert sender.balance == 900.0
        assert recipient.balance == 592.0
