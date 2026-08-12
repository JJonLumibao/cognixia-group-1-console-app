from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ACCOUNT REQUEST SCHEMAS
# Used when customers or authorized employees perform account operations.

class DepositRequest(BaseModel):
    # ID of the account receiving the deposit.
    account_id: str

    # Amount being deposited.
    # The value must be greater than zero.
    amount: float = Field(
        ...,
        gt=0,
        description="Deposit amount must be positive"
    )


class WithdrawRequest(BaseModel):
    # ID of the account receiving the withdrawal.
    account_id: str

    # Amount being withdrawn.
    # The value must be greater than zero.
    amount: float = Field(
        ...,
        gt=0,
        description="Withdrawal amount must be positive"
    )


# ACCOUNT RESPONSE SCHEMA
# Defines the information returned when an account is requested.
class AccountResponse(BaseModel):
    # Unique account identifier.
    id: str  # Updated to str to match MongoDB / Domain IDs

    # ID of the customer who owns the account.
    owner_id: str  # Updated from customer_id to match our Account class

    # Account type, such as Checking or Savings.
    account_type: str

    # Current account balance.
    balance: float

    # Branch associated with the account.
    branch_id: str

    # Indicates whether the account is active.
    active: bool = True


# ACCOUNT STATUS UPDATE SCHEMA
# Used to activate or deactivate an individual bank account.
class AccountStatusUpdate(BaseModel):
    active: bool


# ACCOUNT CREATE SCHEMA
# Defines the information required to create a new bank account.
class AccountCreate(BaseModel):
    # Customer who will own the account.
    owner_id: str

    # Type of account being created.
    account_type: str  # e.g., "Checking" or "Savings"

    # Starting balance for the new account.
    balance: float = 0.00

    # Branch associated with the account.
    branch_id: str

    # Optional fields to handle our specific child classes.
    min_balance: Optional[float] = 100.0  # For SavingsAccount
    overdraft_limit: Optional[float] = 500.0  # For CheckingAccount


# TRANSACTION RESPONSE SCHEMA
# Defines the information returned for a completed transaction.
class TransactionResponse(BaseModel):
    # Unique transaction identifier.
    id: str

    # Link back to the original transaction request for audit tracking.
    # This makes it easy to correlate completed or rejected transactions
    # with the pending request that generated them.
    request_id: Optional[str] = None

    # Account money was taken from.
    # Optional because deposits do not have a source account.
    from_account_id: Optional[str] = None

    # Account money was sent to.
    # Optional because withdrawals do not have a destination account.
    to_account_id: Optional[str] = None

    # Amount involved in the transaction.
    amount: float

    # Type of transaction: Deposit, Withdrawal, or Transfer.
    type: str

    # Status of the transaction.
    status: str

    # Date and time when the transaction occurred.
    timestamp: datetime


# Request model used to capture pending deposit/withdrawal/transfer operations.
class TransactionRequestCreate(BaseModel):
    request_type: str
    from_account_id: Optional[str] = None
    to_account_id: Optional[str] = None
    amount: float = Field(
        ..., gt=0, description="Request amount must be positive"
    )


# Response model includes the request status and branch visibility metadata.
class TransactionRequestResponse(BaseModel):
    id: str
    request_type: str
    from_account_id: Optional[str] = None
    to_account_id: Optional[str] = None
    amount: float
    status: str
    requested_by: str
    branch_id: Optional[str] = None
    destination_branch_id: Optional[str] = None
    transaction_id: Optional[str] = None
    requested_at: datetime


# CUSTOMER RESPONSE SCHEMA
# Defines the information returned for a customer.
class CustomerResponse(BaseModel):
    id: str
    name: str
    email: str
    branch_id: str
    active: bool

    # List of account IDs belonging to the customer.
    accounts: List[str] = []

    # List of transaction IDs associated with the customer's accounts.
    transactions: List[str] = []


# CUSTOMER CREATE SCHEMA
# Defines the information required to create a new customer.
class CustomerCreate(BaseModel):
    """Schema for creating a new customer."""

    first_name: str
    last_name: str
    email: str
    branch_id: str


# CUSTOMER UPDATE SCHEMA
# Defines optional fields that can be changed for an existing customer.
class CustomerUpdate(BaseModel):
    """Schema for updating an existing customer. All fields are optional."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    branch_id: Optional[str] = None
    active: Optional[bool] = None


# TRANSFER REQUEST SCHEMA
# Defines the information required to transfer money between accounts.
class TransferCreate(BaseModel):
    """Schema specifically for account-to-account transfers."""

    # Account sending the money.
    from_account_id: str

    # Account receiving the money.
    to_account_id: str

    # Amount being transferred.
    amount: float


# REGISTRATION SCHEMA
# Defines the information required when creating a user account.
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

    # Defaults newly registered users to the CUSTOMER role.
    role: str = "CUSTOMER"

    # Optional branch assignment for branch-specific users.
    branch_id: Optional[str] = None


# BRANCH CREATE SCHEMA
# Defines the information required to create a new bank branch.
class BranchCreate(BaseModel):
    branch_code: str
    branch_name: str
    location: str
    manager_id: str

    # Staff IDs can be stored as a comma-separated string.
    staff_list: Optional[str] = None


# BRANCH PERFORMANCE METRICS
# Stores account and balance statistics for a branch.
class BranchPerformance(BaseModel):
    total_accounts: int
    active_accounts: int
    total_balance: float


# STAFF METRICS
# Stores staffing statistics for a branch.
class StaffMetrics(BaseModel):
    total_staff: int
    total_tellers: int


# BRANCH RESPONSE WITH METRICS
# Returns branch information along with optional performance and staff statistics.
class BranchResponse(BaseModel):
    branch_code: str
    branch_name: str
    location: str
    manager_id: Optional[str] = None
    staff_list: Optional[str] = None

    # Optional performance information for the branch.
    performance: Optional[BranchPerformance] = None

    # Optional staffing information for the branch.
    staff_metrics: Optional[StaffMetrics] = None


# BRANCH MANAGER UPDATE SCHEMA
# Used by administrators to assign a different branch manager.
class BranchManagerUpdate(BaseModel):
    manager_id: str


# LOGIN SCHEMA
# Defines the credentials used when authenticating a user.
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# TOKEN RESPONSE SCHEMA
# Defines the authentication tokens returned after successful login.
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

    # Specifies that the returned access token uses bearer authentication.
    token_type: str = "bearer"


# USER RESPONSE SCHEMA
# Defines the public user information returned by the API.
class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    active: bool