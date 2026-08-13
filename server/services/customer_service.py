from sqlalchemy import select, or_
from models.database import (
    SessionLocal,
    Customer as CustomerORM,
    Transaction as TransactionORM,
    generate_customer_id,
)


def _transaction_ids_for_accounts(session, account_ids: list[str]) -> list[str]:
    if not account_ids:
        return []

    stmt = select(TransactionORM.id).where(
        or_(
            TransactionORM.from_account_id.in_(account_ids),
            TransactionORM.to_account_id.in_(account_ids)
        )
    )
    return session.scalars(stmt).all()


# Retrieve all customers from the database.
def get_all_customers() -> list:
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
                "transactions": _transaction_ids_for_accounts(
                    session,
                    [account.id for account in customer.accounts]
                ),
            }
            for customer in customers
        ]


# Retrieve the customer associated with the currently logged-in user's email.
def get_customer_by_email(email: str) -> dict:

    with SessionLocal() as session:

        customer = session.execute(
            select(CustomerORM).where(
                CustomerORM.email == email
            )
        ).scalar_one_or_none()

        # Make sure a customer profile exists for the authenticated user.
        if not customer:
            raise ValueError(
                "Customer profile not found for this user."
            )

        account_ids = [account.id for account in customer.accounts]

        return {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "branch_id": customer.branch_id,
            "active": customer.active,
            "accounts": account_ids,
            "transactions": _transaction_ids_for_accounts(session, account_ids),
        }


# Retrieve a specific customer using their customer ID.
def get_customers_by_id(customer_id: str) -> dict:

    with SessionLocal() as session:
        customer = session.get(CustomerORM, customer_id)

        # Return an error if the requested customer does not exist.
        if not customer:
            raise ValueError(
                f"Customer with ID {customer_id} not found."
            )

        return {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "branch_id": customer.branch_id,
            "active": customer.active,
            "accounts": [account.id for account in customer.accounts],
        }


# Create a new customer and save the customer to the database.
def create_customer(customer_data: dict) -> dict:

    # Generate a hashed ID for the new customer.
    new_id = generate_customer_id()

    # Combine first and last name into the database's single name field.
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

    # Return the newly created customer's information.
    return get_customers_by_id(new_id)


# Update specific fields for an existing customer.
def update_customer(customer_id: str, updated_data: dict) -> dict:

    with SessionLocal() as session:
        customer = session.get(CustomerORM, customer_id)

        # Make sure the customer exists before attempting an update.
        if not customer:
            raise ValueError(
                f"Customer with ID {customer_id} not found."
            )

        # Map Pydantic first_name/last_name into the ORM `name` column.
        first = updated_data.pop("first_name", None)
        last = updated_data.pop("last_name", None)

        if first is not None or last is not None:
            # Preserve the existing name portion when only first or last name is updated.
            existing = (customer.name or "").strip()
            parts = existing.split(" ", 1) if existing else []
            existing_first = parts[0] if len(parts) >= 1 else ""
            existing_last = parts[1] if len(parts) == 2 else ""

            new_first = first if first is not None else existing_first
            new_last = last if last is not None else existing_last

            customer.name = f"{new_first} {new_last}".strip()

        # Apply any remaining fields directly to the matching customer columns.
        for field, value in updated_data.items():
            setattr(customer, field, value)

        session.commit()
        session.refresh(customer)

    # Return the updated customer.
    return get_customers_by_id(customer_id)


# Deactivate a customer and all accounts belonging to that customer.
def deactivate_customer(customer_id: str) -> dict:

    with SessionLocal() as session:
        customer = session.get(CustomerORM, customer_id)

        # Make sure the customer exists before deactivating them.
        if not customer:
            raise ValueError(
                f"Customer with ID {customer_id} not found."
            )

        # Soft-delete the customer by marking them as inactive.
        customer.active = False

        # Deactivate all accounts belonging to the customer.
        for account in customer.accounts:
            account.active = False

        session.commit()
        session.refresh(customer)

    # Return the updated customer information.
    return get_customers_by_id(customer_id)