import os
import uuid
import hashlib
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


# DATABASE CONFIGURATION
# Load environment variables from the .env file.
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Make sure the database connection string exists before starting the application.
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing. Please ensure your .env file is set up.")


# Create the SQLAlchemy database engine.
# The engine manages connections between the application and PostgreSQL.
engine = create_engine(DATABASE_URL, echo=False, future=True)

# Create a reusable database session factory.
# Each service can use SessionLocal() when it needs to interact with the database.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
    future=True
)

# Base class used by all SQLAlchemy database models.
Base = declarative_base()


# ID GENERATION
# Generate a short unique identifier for database records.
def generate_id() -> str:
    return uuid.uuid4().hex[:12]


# Generate a customer identifier using a hashed form for additional obscurity.
# This is separate from transaction/account IDs so customer IDs can be treated differently.
def generate_customer_id() -> str:
    raw_id = uuid.uuid4().hex
    return hashlib.sha256(raw_id.encode("utf-8")).hexdigest()


# USER DATABASE MODEL
# Stores authentication and authorization information for application users.
class User(Base):
    __tablename__ = "users"

    # Unique identifier for the user.
    id = Column(String, primary_key=True, index=True)

    # User's email address used for authentication.
    email = Column(String, nullable=False, unique=True, index=True)

    # Hashed password stored instead of the user's plain-text password.
    password_hash = Column(String, nullable=False)

    # Determines what permissions the user has in the application.
    role = Column(String, nullable=False, default="CUSTOMER")

    # Branch associated with the user, if applicable.
    branch_id = Column(String, nullable=True)

    # Determines whether the user account is currently active.
    active = Column(Boolean, nullable=False, default=True)


# CUSTOMER DATABASE MODEL
# Stores information about bank customers.
class Customer(Base):
    __tablename__ = "customers"

    # Unique identifier for the customer.
    id = Column(String, primary_key=True, index=True)

    # Customer's name.
    name = Column(String, nullable=False)

    # Customer's email address.
    email = Column(String, nullable=False, unique=True)

    # Branch associated with the customer.
    branch_id = Column(String, nullable=True)

    # Determines whether the customer is currently active.
    active = Column(Boolean, nullable=False, default=True)

    # Relationship allowing a customer to have multiple bank accounts.
    accounts = relationship(
        "Account",
        back_populates="owner",
        cascade="all, delete-orphan"
    )


# ACCOUNT DATABASE MODEL
# Stores individual bank accounts belonging to customers.
class Account(Base):
    __tablename__ = "accounts"

    # Unique identifier for the account.
    id = Column(String, primary_key=True, index=True)

    # ID of the customer who owns this account.
    owner_id = Column(String, ForeignKey("customers.id"), nullable=False)

    # Type of account, such as Checking or Savings.
    account_type = Column(String, nullable=False)

    # Current monetary balance of the account.
    balance = Column(Float, nullable=False, default=0.0)

    # Branch associated with the account.
    branch_id = Column(String, nullable=True)

    # Determines whether the account is currently active.
    active = Column(Boolean, nullable=False, default=True)

    # Relationship connecting the account back to its customer owner.
    owner = relationship("Customer", back_populates="accounts")


# TRANSACTION DATABASE MODEL
# Stores deposits, withdrawals, and account-to-account transfers.
class Transaction(Base):
    __tablename__ = "transactions"

    # Unique identifier for the transaction.
    id = Column(String, primary_key=True, index=True)

    # Optional link back to a transaction request if this transaction
    # started as a pending request.
    request_id = Column(String, ForeignKey("transaction_requests.id"), nullable=True)

    # Account money is being taken from.
    # Nullable because deposits do not have a source account.
    from_account_id = Column(
        String,
        ForeignKey("accounts.id"),
        nullable=True
    )

    # Account money is being sent to.
    # Nullable because withdrawals do not have a destination account.
    to_account_id = Column(
        String,
        ForeignKey("accounts.id"),
        nullable=True
    )

    # Amount of money involved in the transaction.
    amount = Column(Float, nullable=False)

    # Type of transaction: Deposit, Withdrawal, or Transfer.
    type = Column(String, nullable=False)

    # Status of the transaction record.
    # This allows tracking whether a transaction is completed or still pending.
    status = Column(String, nullable=False, default="Completed")

    # Date and time when the transaction was created.
    timestamp = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )


class TransactionRequest(Base):
    __tablename__ = "transaction_requests"

    id = Column(String, primary_key=True, index=True)
    request_type = Column(String, nullable=False)
    from_account_id = Column(
        String,
        ForeignKey("accounts.id"),
        nullable=True
    )
    to_account_id = Column(
        String,
        ForeignKey("accounts.id"),
        nullable=True
    )
    amount = Column(Float, nullable=False)
    status = Column(String, nullable=False, default="Pending")
    requested_by = Column(String, nullable=False)
    branch_id = Column(String, nullable=True)
    destination_branch_id = Column(String, nullable=True)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=True)
    requested_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )


# BRANCH DATABASE MODEL
# Stores information about bank branches and their managers/staff.
class Branch(Base):
    __tablename__ = "branches"

    # Unique branch code used to identify the branch.
    branch_code = Column(String, primary_key=True, index=True)

    # Name of the branch.
    branch_name = Column(String, nullable=False)

    # Physical location of the branch.
    location = Column(String, nullable=False)

    # ID of the user assigned as the branch manager.
    manager_id = Column(String, nullable=False)

    # Comma-separated list of staff IDs associated with the branch.
    staff_list = Column(String, nullable=True)


# DATABASE INITIALIZATION
# Create all database tables defined by the SQLAlchemy models.
def init_db() -> None:
    Base.metadata.create_all(bind=engine)