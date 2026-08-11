from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class DepositRequest(BaseModel):
    # Field(gt=0) enforces the amount must be greater than 0 at the API level
    amount: float = Field(..., gt=0, description="Deposit amount must be positive")

class WithdrawRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Withdrawal amount must be positive")

class AccountResponse(BaseModel):
    id: str  # Updated to str to match MongoDB / Domain IDs
    owner_id: str  # Updated from customer_id to match our Account class
    account_type: str
    balance: float
    branch_id: str 
    active: bool = True

class AccountCreate(BaseModel):
    owner_id: str
    account_type: str  # e.g., "Checking" or "Savings"
    balance: float = 0.00
    branch_id: str
    
    # Optional fields to handle our specific child classes
    min_balance: Optional[float] = 100.0        # For SavingsAccount
    overdraft_limit: Optional[float] = 500.0    # For CheckingAccount

class TransferRequest(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: float = Field(..., gt=0)

class TransactionResponse(BaseModel):
    id: str
    # Made optional because deposits/withdrawals only use one of these
    from_account_id: Optional[str] = None 
    to_account_id: Optional[str] = None
    amount: float
    type: str  # "Deposit", "Withdrawal", or "Transfer"
    timestamp: datetime  # Updated from string to native datetime

class CustomerResponse(BaseModel):
    id: str
    name: str
    email: str
    branch_id: str
    active: bool
    accounts: List[str] = []   

class CustomerCreate(BaseModel):
    """Schema for creating a new customer"""
    first_name: str
    last_name: str
    email: str
    branch_id: str

class CustomerUpdate(BaseModel):
    """Schema for updating an existing customer. All fields are optional."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    branch_id: Optional[str] = None
    active: Optional[bool] = None

class TransactionCreate(BaseModel):
    """Schema for creating a new transaction"""
    from_account: Optional[str] = None
    to_account: Optional[str] = None
    amount: float
    transaction_type: str

class TransferCreate(BaseModel):
    """Schema specifically for account-to-account transfers"""
    from_account_id: str
    to_account_id: str
    amount: float

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = "CUSTOMER"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"