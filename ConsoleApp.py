from abc import ABC, abstractmethod
class BankAccount(ABC):
    def __init__(self, owner: str):
        self.owner = owner
        self._balance = 0.0
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
            raise ValueError("Withdrawal amount must be positive and less than or equal to the balance.")

    @property
    def accrued_interest(self) -> float:
        return self._balance * self.interest_rate

    @property    
    @abstractmethod
    def get_balance(self) -> float:
        pass

    

class SavingsAccount(BankAccount):
    def __init__(self, owner: str, interest_rate: float):
        super().__init__(owner)
        self.interest_rate = interest_rate

    @property
    def get_balance(self) -> float:
        return self._balance + (self._balance * self.interest_rate)


class CheckingAccount(BankAccount):
    @property
    def get_balance(self) -> float:
        return self._balance


def main():
    savings = SavingsAccount("Alice", 0.20)
    checking = CheckingAccount("Bob")

    savings.deposit(1000)
    checking.deposit(500)

    accounts = [savings, checking]

    for account in accounts:
        print(f"{account.owner}'s account type: {type(account).__name__}")
        print(f"Interest Rate: {account.interest_rate * 100:.2f}%")
        print(f"Accrued Interest: ${account.accrued_interest:.2f}")
        print(f"{account.owner}'s account balance: ${account.get_balance:.2f}")

        account.withdraw(100)
        print(f"{account.owner}'s account balance after withdrawal: ${account.get_balance:.2f}")

if __name__ == "__main__":
    main()