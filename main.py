"""
Entry point for data management system REST API (FastAPI).

This file is responsible ONLY for:
  - creating the FastAPI app instance
  - wiring together the routers built by the controllers/ layer
  - app-level metadata and a health check

"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from controllers.customer_controller import router as customer_router
from controllers.account_controller import router as account_router
from controllers.transaction_controller import router as transaction_router
from controllers.auth_controller import router as auth_router
from controllers.branch_manager_controller import router as branch_manager_router
from controllers.user_controller import router as user_router

from models.database import init_db

app = FastAPI(
    title="Bank Management System API",
    description="RESTful API for managing customers, accounts, and transactions.",
    version="1.0.0",
)

# Allow the local frontend dev server to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables automatically if they do not yet exist.
init_db()

# Each controller module owns its own routes; main.py just registers
# them under the versioned prefix + tag from the roadmap spec.
app.include_router(customer_router, prefix="/api/v1/customers", tags=["Customers"])
app.include_router(account_router, prefix="/api/v1/accounts", tags=["Accounts"])
app.include_router(transaction_router, prefix="/api/v1/transactions", tags=["Transactions"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(branch_manager_router, prefix="/api/v1/branch-managers", tags=["Branch Managers"])
app.include_router(user_router, prefix="/api/v1/users", tags=["Users"])

@app.get("/", tags=["Health"])
def health_check():
    """Simple liveness check to confirm the API is up."""
    return {"status": "ok", "service": "Bank Management System API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)