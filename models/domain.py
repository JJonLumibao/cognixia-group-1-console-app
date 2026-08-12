from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import List, Optional
import uuid


# TRANSACTION TYPES
# Defines the types of financial transactions supported by the application.
class TransactionType(Enum):

    DEPOSIT = "Deposit"
    WITHDRAWAL = "Withdrawal"
    TRANSFER = "Transfer"


# TRANSACTION DOMAIN MODEL
# Represents a financial transaction between bank accounts.
class Transaction:

    def __init__(
        self,
        from_account: Optional[str],
        to_account: Optional[str],
        amount: float,
        transaction_type: TransactionType
    ):
        # Generate a unique identifier for the transaction.
        self.transaction_id: str = uuid.uuid4().hex[:12]

        # Store the source account.
        # This can be None for deposits.
        self.from_account_id = from_account

        # Store the destination account.
        # This can be None for withdrawals.
        self.to_account_id = to_account

        # Store the amount involved in the transaction.
        self.amount = amount

        # Store the type of transaction.
        self.type = transaction_type

        # Record when the transaction was created.
        self.timestamp = datetime.utcnow()


# CUSTOMER DOMAIN MODEL
# Represents a bank customer and the accounts associated with them.
class Customer:

    def __init__(
        self,
        customer_id: str,
        name: str,
        email: str,
        branch_id: str,
        active: bool = True
    ):
        # Store the customer's unique identifier.
        self.id = customer_id

        # Store the customer's name and email.
        self.name = name
        self.email = email

        # Store the branch associated with the customer.
        self.branch_id = branch_id

        # Track whether the customer is active.
        self.active = active

        # Store the IDs of the customer's accounts.
        # A customer can have multiple accounts.
        self.accounts: List[str] = []


# BRANCH DOMAIN MODEL
# Represents a bank branch and its manager/staff information.
class Branch:

    def __init__(
        self,
        branch_code: str,
        branch_name: str,
        location: str,
        manager_id: str,
        staff_list: List[str]
    ):
        # Store the branch's identifying information.
        self.branch_code = branch_code
        self.branch_name = branch_name
        self.location = location

        # Store the ID of the branch manager.
        self.manager_id = manager_id

        # Store the staff members assigned to the branch.
        self.staff_list = staff_list


# BANK ACCOUNT BASE CLASS
# Defines shared behavior for all bank account types.
class BankAccount(ABC):

    def __init__(
        self,
        account_number: str,
        account_type: str,
        balance: float,
        owner_id: str
    ):
        # Store the account's identifying information.
        self.account_number = account_number
        self.account_type = account_type

        # The balance is protected so subclasses can control how it is accessed.
        self._balance = balance

        # Store the ID of the customer who owns the account.
        self.owner_id = owner_id

        # Default interest rate is zero.
        # SavingsAccount overrides this value.
        self.interest_rate = 0.0

        # Store transactions performed on this account.
        self.transaction_history: List[Transaction] = []

    # DEPOSIT
    # Add money to the account and record the deposit as a transaction.
    def deposit(self, amount: float) -> None:

        if amount > 0:
            self._balance += amount

            self.transaction_history.append(
                Transaction(
                    from_account=None,
                    to_account=self.account_number,
                    amount=amount,
                    transaction_type=TransactionType.DEPOSIT
                )
            )
        else:
            raise ValueError("Deposit amount must be positive.")

    # WITHDRAWAL
    # Remove money from the account if the account has enough funds.
    def withdraw(self, amount: float) -> None:

        if 0 < amount <= self._balance:
            self._balance -= amount

            self.transaction_history.append(
                Transaction(
                    from_account=self.account_number,
                    to_account=None,
                    amount=amount,
                    transaction_type=TransactionType.WITHDRAWAL
                )
            )
        else:
            raise ValueError(
                "Withdrawal amount must be positive and less than or equal to the balance."
            )

    # ACCRUED INTEREST
    # Calculate interest based on the account's current balance.
    @property
    def accrued_interest(self) -> float:
        return self._balance * self.interest_rate

    # BALANCE
    # Each account type must provide its own implementation of get_balance().
    @property
    @abstractmethod
    def get_balance(self) -> float:
        pass


# SAVINGS ACCOUNT
# Extends BankAccount with an interest rate.
class SavingsAccount(BankAccount):

    def __init__(
        self,
        account_number: str,
        balance: float,
        owner_id: str,
        interest_rate: float
    ):
        # Initialize the common BankAccount properties.
        super().__init__(
            account_number,
            "Savings",
            balance,
            owner_id
        )

        # Store the savings account's interest rate.
        self.interest_rate = interest_rate

    # BALANCE
    # Savings accounts include accrued interest in the visible balance.
    @property
    def get_balance(self) -> float:
        return self._balance + (self._balance * self.interest_rate)


# CHECKING ACCOUNT
# Extends BankAccount without applying interest by default.
class CheckingAccount(BankAccount):

    def __init__(
        self,
        account_number: str,
        balance: float,
        owner_id: str
    ):
        # Initialize the common BankAccount properties.
        super().__init__(
            account_number,
            "Checking",
            balance,
            owner_id
        )

    # BALANCE
    # Checking accounts return their current balance directly.
    @property
    def get_balance(self) -> float:
        return self._balance