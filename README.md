# JADE Bank Management System

A full-stack bank management system developed collaboratively by a team of four as part of the Collabera/Cognixia training program.

The application simulates a real-world banking environment with role-based authorization, multi-currency accounts, transaction workflows, and customer-to-teller transaction requests.

## Tech Stack

### Frontend
- React
- JavaScript
- Vite
- React Router
- Axios

### Backend
- Python
- FastAPI
- SQLAlchemy
- Pydantic
- JWT Authentication
- bcrypt

### Database
- PostgreSQL

### Development Tools
- Git / GitHub
- Postman
- VS Code

## Key Features

### Role-Based Authorization

The system implements role-based access control with four distinct user roles, each with different permissions and responsibilities:

- **Customer** - Manage personal accounts and submit deposit/withdrawal requests.
- **Teller** - Manage deposits, withdrawals, review customer transaction requests, and approve or reject deposit and withdrawal requests. 
- **Branch Manager** - Manage branch operations and oversee branch-level activity.
- **Admin** - Manage users and system-wide banking operations.

Users are only given access to functionality authorized for their assigned role.

### Multi-Currency Banking

A major feature of the application is its multi-currency support. Customers can create accounts using different currency types and maintain accounts in multiple currencies.

The transaction system also supports **currency exchange between accounts**, allowing transactions involving different currencies to be converted appropriately rather than limiting customers to a single currency.

### Customer-to-Teller Transaction Workflow

Instead of allowing customers to directly execute every banking transaction, the system models a real-world teller approval workflow.

Customers can submit:

- Deposit requests
- Withdrawal requests

Tellers can then review each request and:

- **Approve** the transaction
- **Reject** the transaction

This creates a controlled transaction workflow while providing customers with visibility into their transaction requests.

## Project Structure

```text
Collabera Training/
├── client/                 # React frontend
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│
├── server/                 # FastAPI backend
│   ├── controllers/
│   ├── models/
│   ├── security/
│   ├── services/
│   ├── tests/
│   ├── __init__.py
│   ├── .env-example
│   ├── main.py
│   ├── requirements.txt
│   └── seed_db.py
│
├── .gitignore
└── README.md