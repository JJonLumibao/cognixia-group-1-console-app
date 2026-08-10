from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional
import uuid


class TransactionType(Enum):
    DEPOSIT = "Deposit"
    WITHDRAWAL = "Withdrawal"
    TRANSFER = "Transfer"


class Transaction:
    def __init__(self, from_account: Optional[str], to_account: Optional[str],
                 amount: float, transaction_type: TransactionType):
        self.transaction_id: str = str(uuid.uuid4())[:8]
        self.from_account = from_account
        self.to_account = to_account
        self.amount = amount
        self.timestamp: datetime = datetime.now()
        self.type = transaction_type

    def __str__(self) -> str:
        ts = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        if self.type == TransactionType.DEPOSIT:
            return f"[{self.transaction_id}] {ts} | DEPOSIT    | -> {self.to_account} | ${self.amount:.2f}"
        elif self.type == TransactionType.WITHDRAWAL:
            return f"[{self.transaction_id}] {ts} | WITHDRAWAL | {self.from_account} -> | ${self.amount:.2f}"
        else:
            return (f"[{self.transaction_id}] {ts} | TRANSFER   | "
                    f"{self.from_account} -> {self.to_account} | ${self.amount:.2f}")



class Branch:
    def __init__(self, branch_code: str, branch_name: str, Location: str, Manager_ID: str, staff_list: List[str]):
        self.branch_code = branch_code
        self.branch_name = branch_name
        self.Location = Location
        self.Manager_ID = Manager_ID
        self.staff_list = staff_list

class BankAccount(ABC):
    def __init__(self, account_number: str, account_type: str, balance: float, owner_id: str):
        self.account_number = account_number
        self.account_type = account_type
        self._balance = balance
        self.owner_id = owner_id
        self.interest_rate = 0.0
        self.transaction_history: List[Transaction] = []

    def deposit(self, amount: float) -> None:
        if amount > 0:
            self._balance += amount
            self.transaction_history.append(
                Transaction(from_account=None, to_account=self.account_number,
                            amount=amount, transaction_type=TransactionType.DEPOSIT)
            )
        else:
            raise ValueError("Deposit amount must be positive.")

    def withdraw(self, amount: float) -> None:
        if amount > 0 and amount <= self._balance:
            self._balance -= amount
            self.transaction_history.append(
                Transaction(from_account=self.account_number, to_account=None,
                            amount=amount, transaction_type=TransactionType.WITHDRAWAL)
            )
        else:
            raise ValueError(
                "Withdrawal amount must be positive and less than or equal to the balance.")

    def transfer_to(self, other: "BankAccount", amount: float) -> None:
        if amount <= 0 or amount > self._balance:
            raise ValueError("Transfer amount must be positive and less than or equal to the balance.")
        self._balance -= amount
        other._balance += amount
        txn = Transaction(from_account=self.account_number, to_account=other.account_number,
                           amount=amount, transaction_type=TransactionType.TRANSFER)
        self.transaction_history.append(txn)
        other.transaction_history.append(txn)

    def print_transaction_history(self) -> None:
        print(f"  History for {self.account_number}:")
        if not self.transaction_history:
            print("    No transactions yet.")
        for txn in self.transaction_history:
            print(f"    {txn}")

    @property
    def accrued_interest(self) -> float:
        return self._balance * self.interest_rate

    @property
    @abstractmethod
    def get_balance(self) -> float:
        pass


class SavingsAccount(BankAccount):
    def __init__(self, account_number: str, balance: float, owner_id: str, interest_rate: float):
        super().__init__(account_number, "Savings", balance, owner_id)
        self.interest_rate = interest_rate

    @property
    def get_balance(self) -> float:
        return self._balance + (self._balance * self.interest_rate)


class CheckingAccount(BankAccount):
    def __init__(self, account_number: str, balance: float, owner_id: str):
        super().__init__(account_number, "Checking", balance, owner_id)

    @property
    def get_balance(self) -> float:
        return self._balance


class BankingSystem:
    def __init__(self):
        self.branches: Dict[str, Branch] = {}
        self.accounts: Dict[str, BankAccount] = {}

    def add_branch(self, branch: Branch):
        self.branches[branch.branch_code] = branch

class Customer:
    def __init__(self, customer_id: str, name: str, email: str, branch_ID: str):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.account_list = list[BankAccount] = []
        self.branch_ID = branch_ID

    def get_Accounts(self) -> List[BankAccount]:
        return self.account_list
    
    def add_account(self, account: BankAccount) -> None:
        self.account_list.append(account)

    def remove_account(self, account: BankAccount) -> None:
        if account in self.account_list:
            self.account_list.remove(account)
        else:
            raise ValueError("Account not found in the customer's account list.")

    def diplay_customer_info(self) -> None:
        print(f"Customer ID: {self.customer_id}")
        print(f"Name: {self.name}")
        print(f"Email: {self.email}")
        print("Accounts:")
        for account in self.account_list:
            print(f"  - Account Type: {type(account).__name__}, Balance: ${account.get_balance:.2f}")
    
def main():
    banking_system = BankingSystem()
    branch1 = Branch("001", "Downtown Branch", "123 Main St",
                     "MGR001", ["Staff1", "Staff2"])
    branch2 = Branch("002", "Uptown Branch", "456 Elm St",
                     "MGR002", ["Staff3", "Staff4"])
    banking_system.add_branch(branch1)
    banking_system.add_branch(branch2)

    savings = SavingsAccount("SA001", 0, "Alice", 0.02)
    checking = CheckingAccount("CA001", 0, "Bob")

    savings.deposit(1000)
    checking.deposit(500)

    accounts = [savings, checking]

    for account in accounts:
        print(f"{account.owner_id}'s account type: {type(account).__name__}")

        if account.interest_rate > 0:
            print(f"Interest Rate: {account.interest_rate * 100:.2f}%")
            print(f"Accrued Interest: ${account.accrued_interest:.2f}")

        print(
            f"{account.owner_id}'s account balance before withdrawal: ${account.get_balance:.2f}")

        account.withdraw(100)
        print(
            f"{account.owner_id}'s account balance after withdrawal: ${account.get_balance:.2f}")


if __name__ == "__main__":
    main()
