import os
import uuid
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

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing. Please ensure your .env file is set up.")

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, future=True)
Base = declarative_base()

def generate_id() -> str:
    """Generate a stable short identifier for database records."""
    return uuid.uuid4().hex[:12]

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="CUSTOMER")
    branch_id = Column(String, nullable=True)
    active = Column(Boolean, nullable=False, default=True)

class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    branch_id = Column(String, nullable=True)
    active = Column(Boolean, nullable=False, default=True)

    accounts = relationship("Account", back_populates="owner", cascade="all, delete-orphan")

class Account(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True, index=True)
    owner_id = Column(String, ForeignKey("customers.id"), nullable=False)
    account_type = Column(String, nullable=False)
    balance = Column(Float, nullable=False, default=0.0)
    branch_id = Column(String, nullable=True)
    active = Column(Boolean, nullable=False, default=True)

    owner = relationship("Customer", back_populates="accounts")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True)
    from_account_id = Column(String, ForeignKey("accounts.id"), nullable=True)
    to_account_id = Column(String, ForeignKey("accounts.id"), nullable=True)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

class Branch(Base):
    __tablename__ = "branches"

    branch_code = Column(String, primary_key=True, index=True)
    branch_name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    manager_id = Column(String, nullable=False)
    staff_list = Column(String, nullable=True)


def init_db() -> None:
    """Create tables for the PostgreSQL schema."""
    Base.metadata.create_all(bind=engine)
