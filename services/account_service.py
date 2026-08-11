import uuid
from fastapi import HTTPException
from models.database import MongoManager

# Instantiate the database connection for account operations.
db = MongoManager()

class AccountService:

    @staticmethod
    def create_account(payload):
        # Verify that the customer exists before creating the account.
        customer = db.customers.find_one({"_id": payload.owner_id})
        if customer is None:
            raise HTTPException(status_code=404, detail="Customer not found")

        # Generate a new account ID and persist the account document.
        new_id = str(uuid.uuid4())[:8]
        new_account = {
            "_id": new_id,
            "owner_id": payload.owner_id,
            "account_type": payload.account_type,
            "balance": float(payload.balance),
            "branch_id": payload.branch_id,
            "active": True
        }

        db.accounts.insert_one(new_account)
        db.customers.update_one(
            {"_id": payload.owner_id},
            {"$addToSet": {"accounts": new_id}}
        )

        new_account["id"] = new_account.pop("_id")
        return new_account

    @staticmethod
    def get_accounts(branch_id=None, min_balance=None):
        query = {}

        if branch_id is not None:
            query["branch_id"] = str(branch_id)

        if min_balance is not None:
            query["balance"] = {"$gte": float(min_balance)}

        accounts = list(db.accounts.find(query))
        for account in accounts:
            account["id"] = account.pop("_id")

        return accounts