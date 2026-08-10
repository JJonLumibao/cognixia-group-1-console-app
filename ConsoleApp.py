from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional


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

    def deposit(self, amount: float) -> None:
        if amount > 0:
            self._balance += amount
        else:
            raise ValueError("Deposit amount must be positive.")

    def withdraw(self, amount: float) -> None:
        if amount > 0 and amount <= self._balance:
            self._balance -= amount
        else:
            raise ValueError(
                "Withdrawal amount must be positive and less than or equal to the balance.")

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
