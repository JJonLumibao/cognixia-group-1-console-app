# Bank Management System

A full-stack Bank Management System built as a collaborative project during the Collabera/Cognixia training program.

The application provides a web-based interface for managing customers, accounts, branches, users, and banking transactions.

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

### Development & Tools
- Git / GitHub
- VS Code
- Postman

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
│   ├── .env-example
│   ├── __init__.py
│   ├── main.py
│   ├── seed_db.py
│   └── requirements.txt
│
├── .gitignore
└── README.md