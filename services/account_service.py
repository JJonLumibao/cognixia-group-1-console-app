import uuid
from fastapi import HTTPException
from sqlalchemy import select
from models.database import SessionLocal, Account as AccountORM, Customer as CustomerORM

class AccountService:

    @staticmethod
    def create_account(payload):
        with SessionLocal() as session:
            customer = session.get(CustomerORM, payload.owner_id)
            if customer is None:
                raise HTTPException(status_code=404, detail="Customer not found")

            new_id = str(uuid.uuid4())[:8]
            new_account = AccountORM(
                id=new_id,
                owner_id=payload.owner_id,
                account_type=payload.account_type,
                balance=float(payload.balance),
                branch_id=payload.branch_id,
                active=True,
            )
            session.add(new_account)
            session.commit()
            session.refresh(new_account)

            return {
                "id": new_account.id,
                "owner_id": new_account.owner_id,
                "account_type": new_account.account_type,
                "balance": new_account.balance,
                "branch_id": new_account.branch_id,
                "active": new_account.active,
            }

    @staticmethod
    def get_accounts(branch_id=None, min_balance=None, current_user=None):
        with SessionLocal() as session:

            stmt = select(AccountORM)

            # CUSTOMER can only see their own accounts
            if "CUSTOMER" in current_user.get("roles", []):
                user_email = current_user.get("email")

                customer = session.execute(
                    select(CustomerORM).where(
                        CustomerORM.email == user_email
                    )
                ).scalar_one_or_none()

                if customer is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Customer profile not found"
                    )

                stmt = stmt.where(
                    AccountORM.owner_id == customer.id
                )

            if branch_id is not None:
                stmt = stmt.where(
                    AccountORM.branch_id == str(branch_id)
                )

            if min_balance is not None:
                stmt = stmt.where(
                    AccountORM.balance >= float(min_balance)
                )

            results = session.scalars(stmt).all()

            return [
                {
                    "id": account.id,
                    "owner_id": account.owner_id,
                    "account_type": account.account_type,
                    "balance": account.balance,
                    "branch_id": account.branch_id,
                    "active": account.active,
                }
                for account in results
            ]