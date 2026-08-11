from pydantic import BaseModel

class DepositRequest(BaseModel):
    amount: float

class WithdrawRequest(BaseModel):
    amount: float

class AccountResponse(BaseModel):
    id: int
    customer_id: int
    account_type: str
    balance: float
    branch_id: int
    active: bool

class AccountCreate(BaseModel):
    customer_id: int
    account_type: str
    balance: float = 0.00
    branch_id: int

class TransferRequest(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: float


class TransactionResponse(BaseModel):
    id: int
    from_account_id: int
    to_account_id: int
    amount: float
    type: str
    date: str

class CustomerResponse(BaseModel):
   id: int
   first_name: str
   last_name: str
   email: str
   active: bool
