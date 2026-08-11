import uuid
from models.database import MongoManager
from models.domain import Customer

# Instantiate the database connection
db = MongoManager()

def get_all_customers() -> list:
    """Fetches all customers from the database."""

    customers = list(db.customers.find({}))
    for c in customers:
        c["id"] = c.pop("_id")
    return customers

def get_customers_by_id(customer_id: str) -> dict:
    """Fetches a single customer by their ID."""
    customer = db.customers.find_one({"_id": customer_id})
    if not customer:
        raise ValueError(f"Customer with ID {customer_id} not found.")
    
    customer["id"] = customer.pop("_id")
    return customer

def create_customer(customer_data: dict) -> dict:
    """Creates a new customer domain object and saves it to the database."""
    new_id = str(uuid.uuid4())[:8]
    
    new_customer = Customer(
        customer_id=new_id,
        name=f"{customer_data.get('first_name', '')} {customer_data.get('last_name', '')}".strip(),
        email=customer_data.get("email"),
        branch_id=str(customer_data.get("branch_id", "UNKNOWN")),
        active=True
    )
    
    db.save_customer(new_customer)
    
    return get_customers_by_id(new_id)

def update_customer(customer_id: str, updated_data: dict) -> dict:
    """Updates specific fields of an existing customer."""
  
    existing = db.customers.find_one({"_id": customer_id})
    if not existing:
        raise ValueError(f"Customer with ID {customer_id} not found.")
    
    db.customers.update_one({"_id": customer_id}, {"$set": updated_data})
    
    return get_customers_by_id(customer_id)

def deactivate_customer(customer_id: str) -> dict:
    """Soft-deletes a customer by setting their active status to False."""

    existing = db.customers.find_one({"_id": customer_id})
    if not existing:
        raise ValueError(f"Customer with ID {customer_id} not found.")
    
    db.customers.update_one({"_id": customer_id}, {"$set": {"active": False}})
    
    return get_customers_by_id(customer_id)