from pydantic import BaseModel

class DepositRequest(BaseModel):
    amount: float

class WithdrawRequest(BaseModel):
    amount: float

class AccountResponse(BaseModel):
    account_number: str
    account_type: str
    owner_id: str
    balance: float
    accrued_interest: float