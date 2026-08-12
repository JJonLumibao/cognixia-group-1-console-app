from fastapi import HTTPException
from sqlalchemy import select, func

from models.database import (
    SessionLocal,
    Branch as BranchORM,
    Account as AccountORM,
    User as UserORM,
)


def get_manager_branch(session, current_user):
    """
    Find the branch managed by the currently authenticated user.
    """

    print("CURRENT USER:", current_user)

    user_id = current_user.get("sub")

    print("USER ID FROM TOKEN:", user_id)

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="User ID missing from token"
        )

    branch = session.scalar(
        select(BranchORM)
        .where(BranchORM.manager_id == user_id)
    )

    if not branch:
        raise HTTPException(
            status_code=404,
            detail="No branch assigned to this manager"
        )

    return branch

def get_all_branches() -> list:
    with SessionLocal() as session:
        branches = session.scalars(
            select(BranchORM)
        ).all()

        return [
            {
                "branch_code": branch.branch_code,
                "branch_name": branch.branch_name,
                "location": branch.location,
                "manager_id": branch.manager_id,
                "staff_list": branch.staff_list,
            }
            for branch in branches
        ]

def get_branch_performance(current_user):
    """
    Return performance metadata for the manager's branch.
    """

    with SessionLocal() as session:

        branch = get_manager_branch(session, current_user)

        branch_id = branch.branch_code

        total_accounts = session.scalar(
            select(func.count(AccountORM.id))
            .where(AccountORM.branch_id == branch_id)
        )

        active_accounts = session.scalar(
            select(func.count(AccountORM.id))
            .where(
                AccountORM.branch_id == branch_id,
                AccountORM.active == True
            )
        )

        total_balance = session.scalar(
            select(func.coalesce(func.sum(AccountORM.balance), 0))
            .where(AccountORM.branch_id == branch_id)
        )

        return {
            "branch_code": branch.branch_code,
            "branch_name": branch.branch_name,
            "location": branch.location,
            "total_accounts": total_accounts or 0,
            "active_accounts": active_accounts or 0,
            "total_balance": float(total_balance or 0),
        }


def get_staff_metrics(current_user):
    """
    Return staff metrics for the manager's branch.
    """

    with SessionLocal() as session:

        branch = get_manager_branch(session, current_user)

        branch_id = branch.branch_code

        # Your current User model does NOT have branch_id.
        # Therefore staff_list is the only branch/staff relationship
        # currently available in the schema.
        #
        # If staff_list contains user IDs, you can process them here.

        staff_ids = []

        if branch.staff_list:
            staff_ids = [
                staff_id.strip()
                for staff_id in branch.staff_list.split(",")
                if staff_id.strip()
            ]

        total_staff = len(staff_ids)

        total_tellers = 0

        if staff_ids:
            total_tellers = session.scalar(
                select(func.count(UserORM.id))
                .where(
                    UserORM.id.in_(staff_ids),
                    UserORM.role == "TELLER"
                )
            )

        return {
            "branch_code": branch.branch_code,
            "branch_name": branch.branch_name,
            "total_staff": total_staff,
            "total_tellers": total_tellers or 0,
        }

def create_branch(branch_data: dict) -> dict:
    with SessionLocal() as session:

        # Check if branch already exists
        existing_branch = session.scalar(
            select(BranchORM).where(
                BranchORM.branch_code == branch_data["branch_code"]
            )
        )

        if existing_branch:
            raise ValueError(
                f"Branch with code {branch_data['branch_code']} already exists."
            )

        # Make sure manager exists
        manager = session.get(
            UserORM,
            branch_data["manager_id"]
        )

        if not manager:
            raise ValueError(
                f"User with ID {branch_data['manager_id']} not found."
            )

        # Make sure user is actually a branch manager
        if manager.role != "BRANCH_MANAGER":
            raise ValueError(
                "User must have the BRANCH_MANAGER role."
            )

        new_branch = BranchORM(
            branch_code=branch_data["branch_code"],
            branch_name=branch_data["branch_name"],
            location=branch_data["location"],
            manager_id=branch_data["manager_id"],
            staff_list=branch_data.get("staff_list")
        )

        session.add(new_branch)
        session.commit()
        session.refresh(new_branch)

        return {
            "branch_code": new_branch.branch_code,
            "branch_name": new_branch.branch_name,
            "location": new_branch.location,
            "manager_id": new_branch.manager_id,
            "staff_list": new_branch.staff_list,
        }

def update_branch_manager(branch_code: str, manager_id: str) -> dict:
    with SessionLocal() as session:

        branch = session.scalar(
            select(BranchORM).where(
                BranchORM.branch_code == branch_code
            )
        )

        if not branch:
            raise ValueError(
                f"Branch with code {branch_code} not found."
            )

        manager = session.get(UserORM, manager_id)

        if not manager:
            raise ValueError(
                f"User with ID {manager_id} not found."
            )

        if manager.role != "BRANCH_MANAGER":
            raise ValueError(
                "User must have the BRANCH_MANAGER role."
            )

        branch.manager_id = manager_id

        session.commit()
        session.refresh(branch)

        return {
            "branch_code": branch.branch_code,
            "branch_name": branch.branch_name,
            "location": branch.location,
            "manager_id": branch.manager_id,
            "staff_list": branch.staff_list,
        }