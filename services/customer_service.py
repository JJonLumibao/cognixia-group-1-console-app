import uuid
from sqlalchemy import select
from models.database import SessionLocal, Customer as CustomerORM


def get_all_customers() -> list:
    """Fetches all customers from the database."""
    with SessionLocal() as session:
        customers = session.scalars(select(CustomerORM)).all()
        return [
            {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
                "branch_id": customer.branch_id,
                "active": customer.active,
                "accounts": [account.id for account in customer.accounts],
            }
            for customer in customers
        ]


def get_customers_by_id(customer_id: str) -> dict:
    """Fetches a single customer by their ID."""
    with SessionLocal() as session:
        customer = session.get(CustomerORM, customer_id)
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found.")

        return {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "branch_id": customer.branch_id,
            "active": customer.active,
            "accounts": [account.id for account in customer.accounts],
        }


def create_customer(customer_data: dict) -> dict:
    """Creates a new customer and saves it to the database."""
    new_id = str(uuid.uuid4())[:8]
    full_name = f"{customer_data.get('first_name', '')} {customer_data.get('last_name', '')}".strip()

    new_customer = CustomerORM(
        id=new_id,
        name=full_name,
        email=customer_data.get("email"),
        branch_id=str(customer_data.get("branch_id", "UNKNOWN")),
        active=True,
    )

    with SessionLocal() as session:
        session.add(new_customer)
        session.commit()
        session.refresh(new_customer)

    return get_customers_by_id(new_id)


def update_customer(customer_id: str, updated_data: dict) -> dict:
    """Updates specific fields of an existing customer."""
    with SessionLocal() as session:
        customer = session.get(CustomerORM, customer_id)
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found.")

        for field, value in updated_data.items():
            setattr(customer, field, value)

        session.commit()
        session.refresh(customer)

    return get_customers_by_id(customer_id)


def deactivate_customer(customer_id: str) -> dict:
    """Soft-deletes a customer by setting their active status to False."""
    with SessionLocal() as session:
        customer = session.get(CustomerORM, customer_id)
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found.")

        customer.active = False
        session.commit()
        session.refresh(customer)

    return get_customers_by_id(customer_id)
