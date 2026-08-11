from fastapi import HTTPException
from datetime import datetime

from models.database import MongoManager
from models.domain import Transaction, TransactionType

# Instantiate the database connection
db = MongoManager()

def get_transactions(start_date=None, transaction_type=None) -> list:
    """Fetches transactions from the database, optionally filtering by date or type."""
    query = {}
    
    # Add type filter to the database query if provided
    if transaction_type:
        query["type"] = transaction_type
        
    # Add date filter to the database query if provided
    if start_date:
        if isinstance(start_date, str):
            try:
                # Convert string "YYYY-MM-DD" to a datetime object for MongoDB comparison
                dt = datetime.strptime(start_date, "%Y-%m-%d")
                query["timestamp"] = {"$gte": dt}
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    transactions = list(db.transactions.find(query))
    
    # Format IDs for the Pydantic response
    for t in transactions:
        t["id"] = t.pop("_id")
        
    return transactions

def create_transaction(txn_data: dict) -> dict:
    """Creates a new generic transaction and saves it to MongoDB."""
    
    # 1. Convert string type to Enum
    t_type = TransactionType(txn_data.get("transaction_type"))
    
    # 2. Instantiate the Domain Model 
    new_txn = Transaction(
        from_account=txn_data.get("from_account") or txn_data.get("from_account_id"),
        to_account=txn_data.get("to_account") or txn_data.get("to_account_id"),
        amount=txn_data.get("amount"),
        transaction_type=t_type
    )
    
    # 3. Save to MongoDB
    db.record_transaction(new_txn)
    
    # 4. Fetch and return the newly created record
    saved_txn = db.transactions.find_one({"_id": new_txn.transaction_id})
    if saved_txn:
        saved_txn["id"] = saved_txn.pop("_id")
    
    return saved_txn

def transfer_money(payload: dict) -> dict:
    """Handles moving funds between two accounts and recording the transaction in MongoDB."""
    
    from_account_id = payload.get("from_account_id")
    to_account_id = payload.get("to_account_id")
    amount = payload.get("amount", 0)

    # 1. Base validations
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Transfer amount must be greater than 0")
    if from_account_id == to_account_id:
        raise HTTPException(status_code=400, detail="Cannot transfer money to the same account")

    # 2. Database lookups
    from_account = db.accounts.find_one({"_id": from_account_id})
    if not from_account:
        raise HTTPException(status_code=404, detail="Sender account not found")

    to_account = db.accounts.find_one({"_id": to_account_id})
    if not to_account:
        raise HTTPException(status_code=404, detail="Recipient account not found")

    # 3. Account state validations
    if from_account.get("active", True) is False:
        raise HTTPException(status_code=400, detail="Sender account is inactive")
    if to_account.get("active", True) is False:
        raise HTTPException(status_code=400, detail="Recipient account is inactive")
    if from_account.get("balance", 0) < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # 4. Perform the transfer natively in MongoDB using $inc (increment)
    db.accounts.update_one({"_id": from_account_id}, {"$inc": {"balance": -amount}})
    db.accounts.update_one({"_id": to_account_id}, {"$inc": {"balance": amount}})

    # 5. Create a transaction record using the domain model (Fixed to use payload variables)
    new_txn = Transaction(
        from_account=from_account_id,
        to_account=to_account_id,
        amount=amount,
        transaction_type=TransactionType.TRANSFER
    )
    db.record_transaction(new_txn)

    # 6. Fetch and return the completed transaction
    saved_txn = db.transactions.find_one({"_id": new_txn.transaction_id})
    if saved_txn:
        saved_txn["id"] = saved_txn.pop("_id")
        
    return saved_txn