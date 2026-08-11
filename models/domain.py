from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional
import uuid

class TransactionType(Enum):
    """Enumerates the supported transaction categories."""

    DEPOSIT = "Deposit"
    WITHDRAWAL = "Withdrawal"
    TRANSFER = "Transfer"

class Transaction:
    """Represents a single movement of funds between accounts."""

    def __init__(self, from_account: Optional[str], to_account: Optional[str],
                 amount: float, transaction_type: TransactionType):
        self.transaction_id: str = str(uuid.uuid4())[:8]
        self.from_account = from_account
        self.to_account = to_account
        self.amount = amount
        self.timestamp: datetime = datetime.now()
        self.type = transaction_type

class Branch:
    """Stores metadata for a bank branch and its staff."""

    def __init__(self, branch_code: str, branch_name: str, location: str, manager_id: str, staff_list: List[str]):
        self.branch_code = branch_code
        self.branch_name = branch_name
        self.location = location
        self.manager_id = manager_id
        self.staff_list = staff_list

class BankAccount(ABC):
    """Abstract base class for common account behavior."""

    def __init__(self, account_number: str, account_type: str, balance: float, owner_id: str):
        self.account_number = account_number
        self.account_type = account_type
        self._balance = balance
        self.owner_id = owner_id
        self.interest_rate = 0.0
        self.transaction_history: List[Transaction] = []

    def deposit(self, amount: float) -> None:
        """Deposit a positive amount and record the transaction."""
        if amount > 0:
            self._balance += amount
            self.transaction_history.append(
                Transaction(from_account=None, to_account=self.account_number,
                            amount=amount, transaction_type=TransactionType.DEPOSIT)
            )
        else:
            raise ValueError("Deposit amount must be positive.")

    def withdraw(self, amount: float) -> None:
        """Withdraw from the account if sufficient funds are available."""
        if 0 < amount <= self._balance:
            self._balance -= amount
            self.transaction_history.append(
                Transaction(from_account=self.account_number, to_account=None,
                            amount=amount, transaction_type=TransactionType.WITHDRAWAL)
            )
        else:
            raise ValueError("Withdrawal amount must be positive and less than or equal to the balance.")

    @property
    def accrued_interest(self) -> float:
        """Return the interest accumulated on the current balance."""
        return self._balance * self.interest_rate

    @property
    @abstractmethod
    def get_balance(self) -> float:
        """Derived accounts must provide the current visible balance."""
        pass

class SavingsAccount(BankAccount):
    """Savings account with an interest rate applied to the balance."""

    def __init__(self, account_number: str, balance: float, owner_id: str, interest_rate: float):
        super().__init__(account_number, "Savings", balance, owner_id)
        self.interest_rate = interest_rate

    @property
    def get_balance(self) -> float:
        """Return balance plus accumulated interest."""
        return self._balance + (self._balance * self.interest_rate)

class CheckingAccount(BankAccount):
    """Checking account with no interest rate by default."""

    def __init__(self, account_number: str, balance: float, owner_id: str):
        super().__init__(account_number, "Checking", balance, owner_id)

    @property
    def get_balance(self) -> float:
        """Return the current checking account balance."""
        return self._balance
 
    
@dataclass
class Customer:
   customer_id: int
   first_name: str
   last_name: str
   email: str
   active: bool = True
