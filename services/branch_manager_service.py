from fastapi import HTTPException
from sqlalchemy import select, func

from models.database import (
    SessionLocal,
    Branch as BranchORM,
    Account as AccountORM,
    User as UserORM,
)


# BRANCH LOOKUP
# Find the branch managed by the currently authenticated branch manager.
def get_manager_branch(session, current_user):

    # The JWT stores the authenticated user's ID in the "sub" field.
    user_id = current_user.get("sub")

    # A valid user ID is required to identify the manager's branch.
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="User ID missing from token"
        )

    # Find the branch whose manager_id matches the logged-in user's ID.
    branch = session.scalar(
        select(BranchORM)
        .where(BranchORM.manager_id == user_id)
    )

    # Reject the request if the manager is not assigned to a branch.
    if not branch:
        raise HTTPException(
            status_code=404,
            detail="No branch assigned to this manager"
        )

    return branch


# BRANCH RETRIEVAL
# Retrieve all branches along with their performance and staff metrics.
def get_all_branches() -> list:
    with SessionLocal() as session:

        # Retrieve every branch from the database.
        branches = session.scalars(
            select(BranchORM)
        ).all()

        results = []

        # Calculate metrics for each branch individually.
        for branch in branches:

            # BRANCH PERFORMANCE
            # Count all accounts associated with this branch.
            total_accounts = session.scalar(
                select(func.count(AccountORM.id))
                .where(
                    AccountORM.branch_id == branch.branch_code
                )
            )

            # Count only active accounts associated with this branch.
            active_accounts = session.scalar(
                select(func.count(AccountORM.id))
                .where(
                    AccountORM.branch_id == branch.branch_code,
                    AccountORM.active == True
                )
            )

            # Calculate the combined balance of all accounts in the branch.
            total_balance = session.scalar(
                select(func.coalesce(func.sum(AccountORM.balance), 0))
                .where(
                    AccountORM.branch_id == branch.branch_code
                )
            )

            # STAFF METRICS
            # Convert the comma-separated staff list into individual user IDs.
            staff_ids = []

            if branch.staff_list:
                staff_ids = [
                    staff_id.strip()
                    for staff_id in branch.staff_list.split(",")
                    if staff_id.strip()
                ]

            # The number of staff members is based on the staff IDs listed
            # in the branch's staff_list field.
            total_staff = len(staff_ids)

            total_tellers = 0

            # Count staff members whose role is TELLER.
            if staff_ids:
                total_tellers = session.scalar(
                    select(func.count(UserORM.id))
                    .where(
                        UserORM.id.in_(staff_ids),
                        UserORM.role == "TELLER"
                    )
                )

            # ADD BRANCH TO RESULTS
            # Combine the branch information and calculated metrics
            # into a single response object.
            results.append({
                "branch_code": branch.branch_code,
                "branch_name": branch.branch_name,
                "location": branch.location,
                "manager_id": branch.manager_id,
                "staff_list": branch.staff_list,

                "performance": {
                    "total_accounts": total_accounts or 0,
                    "active_accounts": active_accounts or 0,
                    "total_balance": float(total_balance or 0),
                },

                "staff_metrics": {
                    "total_staff": total_staff,
                    "total_tellers": total_tellers or 0,
                }
            })

        return results


# BRANCH PERFORMANCE
# Calculate account and balance statistics for the manager's branch.
def get_branch_performance(current_user):

    with SessionLocal() as session:

        # Find the branch managed by the authenticated user.
        branch = get_manager_branch(session, current_user)

        branch_id = branch.branch_code

        # Count all accounts belonging to the branch.
        total_accounts = session.scalar(
            select(func.count(AccountORM.id))
            .where(AccountORM.branch_id == branch_id)
        )

        # Count only active accounts belonging to the branch.
        active_accounts = session.scalar(
            select(func.count(AccountORM.id))
            .where(
                AccountORM.branch_id == branch_id,
                AccountORM.active == True
            )
        )

        # Calculate the combined balance of all branch accounts.
        total_balance = session.scalar(
            select(func.coalesce(func.sum(AccountORM.balance), 0))
            .where(AccountORM.branch_id == branch_id)
        )

        # Return the calculated branch performance information.
        return {
            "branch_code": branch.branch_code,
            "branch_name": branch.branch_name,
            "location": branch.location,
            "total_accounts": total_accounts or 0,
            "active_accounts": active_accounts or 0,
            "total_balance": float(total_balance or 0),
        }


# STAFF METRICS
# Calculate staff statistics for the manager's branch.
def get_staff_metrics(current_user):

    with SessionLocal() as session:

        # Find the branch managed by the authenticated user.
        branch = get_manager_branch(session, current_user)

        branch_id = branch.branch_code

        # The current User model does NOT have branch_id.
        # Therefore, staff_list is the only branch/staff relationship
        # currently available in the schema.
        #
        # If staff_list contains user IDs, they can be processed here.

        # Convert the comma-separated staff list into individual user IDs.
        staff_ids = []

        if branch.staff_list:
            staff_ids = [
                staff_id.strip()
                for staff_id in branch.staff_list.split(",")
                if staff_id.strip()
            ]

        # Count the total number of staff IDs assigned to the branch.
        total_staff = len(staff_ids)

        total_tellers = 0

        # Count staff members whose role is TELLER.
        if staff_ids:
            total_tellers = session.scalar(
                select(func.count(UserORM.id))
                .where(
                    UserORM.id.in_(staff_ids),
                    UserORM.role == "TELLER"
                )
            )

        # Return the calculated staff metrics.
        return {
            "branch_code": branch.branch_code,
            "branch_name": branch.branch_name,
            "total_staff": total_staff,
            "total_tellers": total_tellers or 0,
        }


# BRANCH CREATION
# Create a new branch and assign an existing branch manager to it.
def create_branch(branch_data: dict) -> dict:

    with SessionLocal() as session:

        # Check whether a branch with this code already exists.
        existing_branch = session.scalar(
            select(BranchORM).where(
                BranchORM.branch_code == branch_data["branch_code"]
            )
        )

        if existing_branch:
            raise ValueError(
                f"Branch with code {branch_data['branch_code']} already exists."
            )

        # Make sure the selected manager exists as a user.
        manager = session.get(
            UserORM,
            branch_data["manager_id"]
        )

        if not manager:
            raise ValueError(
                f"User with ID {branch_data['manager_id']} not found."
            )

        # Make sure the selected user has the BRANCH_MANAGER role.
        if manager.role != "BRANCH_MANAGER":
            raise ValueError(
                "User must have the BRANCH_MANAGER role."
            )

        # Create the new branch database record.
        new_branch = BranchORM(
            branch_code=branch_data["branch_code"],
            branch_name=branch_data["branch_name"],
            location=branch_data["location"],
            manager_id=branch_data["manager_id"],
            staff_list=branch_data.get("staff_list")
        )

        # Associate the manager with the newly created branch.
        manager.branch_id = branch_data["branch_code"]

        # Save the branch and manager changes.
        session.add(new_branch)
        session.commit()
        session.refresh(new_branch)

        # Return the newly created branch.
        return {
            "branch_code": new_branch.branch_code,
            "branch_name": new_branch.branch_name,
            "location": new_branch.location,
            "manager_id": new_branch.manager_id,
            "staff_list": new_branch.staff_list,
        }


# BRANCH MANAGER UPDATE
# Replace the manager assigned to an existing branch.
def update_branch_manager(
    branch_code: str,
    manager_id: str
) -> dict:

    with SessionLocal() as session:

        # Find the branch that will receive the new manager.
        branch = session.scalar(
            select(BranchORM).where(
                BranchORM.branch_code == branch_code
            )
        )

        if not branch:
            raise ValueError(
                f"Branch with code {branch_code} not found."
            )

        # Find the new manager by their user ID.
        manager = session.get(UserORM, manager_id)

        if not manager:
            raise ValueError(
                f"User with ID {manager_id} not found."
            )

        # Make sure the selected user has the BRANCH_MANAGER role.
        if manager.role != "BRANCH_MANAGER":
            raise ValueError(
                "User must have the BRANCH_MANAGER role."
            )

        # Remove the old manager's branch assignment if they
        # were previously assigned to this branch.
        old_manager = session.get(UserORM, branch.manager_id)

        if old_manager and old_manager.branch_id == branch_code:
            old_manager.branch_id = None

        # Assign the new manager to the branch.
        branch.manager_id = manager_id
        manager.branch_id = branch_code

        # Save the branch and manager changes.
        session.commit()
        session.refresh(branch)

        # Return the updated branch.
        return {
            "branch_code": branch.branch_code,
            "branch_name": branch.branch_name,
            "location": branch.location,
            "manager_id": branch.manager_id,
            "staff_list": branch.staff_list,
        }