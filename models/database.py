# models/database.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Import your domain models
from models.domain import Branch, Customer, BankAccount, Transaction

load_dotenv()

class MongoManager:
    def __init__(self):
        uri = os.getenv("MONGO_URI")
        if not uri:
            raise ValueError("MONGO_URI is missing. Please ensure your .env file is set up.")
            
        self.client = MongoClient(uri)
        self.db = self.client["banking_db"]
        
        self.branches = self.db["branches"]
        self.customers = self.db["customers"]
        self.accounts = self.db["accounts"]
        self.transactions = self.db["transactions"]

    def save_branch(self, branch: Branch) -> None:
        branch_data = {
            "_id": branch.branch_code,
            "location": branch.location,
            "manager_id": branch.manager_id,
            "staff_list": branch.staff_list
        }
        self.branches.update_one({"_id": branch.branch_code}, {"$set": branch_data}, upsert=True)

    def save_customer(self, customer: Customer) -> None:
        customer_data = {
            "_id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "branch_id": customer.branch_id,
            "accounts": customer.accounts
        }
        self.customers.update_one({"_id": customer.id}, {"$set": customer_data}, upsert=True)

    def save_account(self, account: BankAccount) -> None:
        account_data = {
            "_id": account.account_number,
            "owner_id": account.owner_id,
            "balance": account.get_balance,
            "type": account.account_type
        }
        self.accounts.update_one({"_id": account.account_number}, {"$set": account_data}, upsert=True)
        
        self.customers.update_one(
            {"_id": account.owner_id},
            {"$addToSet": {"accounts": account.account_number}} 
        )

    def record_transaction(self, txn: Transaction) -> None:
        txn_data = {
            "_id": txn.transaction_id,
            "from_account_id": txn.from_account_id,
            "to_account_id": txn.to_account_id,      
            "amount": txn.amount,
            "type": txn.type.value if hasattr(txn.type, "value") else txn.type,
            "timestamp": txn.timestamp
        }
        self.transactions.update_one({"_id": txn.transaction_id}, {"$set": txn_data}, upsert=True)