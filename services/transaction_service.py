from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select

from models.database import (
    SessionLocal,
    Transaction as TransactionORM,
    TransactionRequest as TransactionRequestORM,
    Account as AccountORM,
    Customer as CustomerORM,
    generate_id,
)
from models.domain import TransactionType, RequestStatus, TransactionStatus


def _transaction_request_to_dict(request):
    return {
        "id": request.id,
        "request_type": request.request_type,
        "from_account_id": request.from_account_id,
        "to_account_id": request.to_account_id,
        "amount": request.amount,
        "status": request.status,
        "requested_by": request.requested_by,
        "branch_id": request.branch_id,
        "destination_branch_id": request.destination_branch_id,
        "transaction_id": request.transaction_id,
        "requested_at": request.requested_at,
    }


def _enforce_branch_access_for_request(request, current_user):
    if "ADMIN" in current_user.get("roles", []):
        return

    user_branch = current_user.get("branch_id")
    if not user_branch:
        raise ValueError("Branch staff must have a branch assigned")

    visible = (
        request.branch_id == user_branch
        or request.destination_branch_id == user_branch
    )

    if not visible:
        raise ValueError("Request is not visible for your branch")


# Transaction requests are stored separately from executed transactions.
# Branch staff may only view and approve/reject requests for their own branch.
# ADMIN users can see and manage all requests across branches.
def get_transaction_requests(current_user) -> list:
    with SessionLocal() as session:
        stmt = select(TransactionRequestORM)

        if "ADMIN" not in current_user.get("roles", []):
            user_branch = current_user.get("branch_id")
            if not user_branch:
                raise ValueError("Branch staff must have a branch assigned")

            stmt = stmt.where(
                (TransactionRequestORM.branch_id == user_branch)
                | (TransactionRequestORM.destination_branch_id == user_branch)
            )

        requests = session.scalars(stmt).all()
        return [_transaction_request_to_dict(r) for r in requests]


def _validate_request_payload(payload: dict, current_user):
    request_type = payload.get("request_type")
    amount = float(payload.get("amount", 0))
    from_account_id = payload.get("from_account_id")
    to_account_id = payload.get("to_account_id")

    if request_type not in {
        TransactionType.DEPOSIT.value,
        TransactionType.WITHDRAWAL.value,
        TransactionType.TRANSFER.value,
    }:
        raise ValueError("Invalid request type")

    if amount <= 0:
        raise ValueError("Request amount must be greater than 0")

    if request_type == TransactionType.DEPOSIT.value and not to_account_id:
        raise ValueError("Deposit requests require a destination account")

    if request_type == TransactionType.WITHDRAWAL.value and not from_account_id:
        raise ValueError("Withdrawal requests require a source account")

    if request_type == TransactionType.TRANSFER.value:
        if not from_account_id or not to_account_id:
            raise ValueError("Transfer requests require both source and destination accounts")
        if from_account_id == to_account_id:
            raise ValueError("Cannot transfer to the same account")

    return request_type, from_account_id, to_account_id, amount


def create_transaction_request(payload: dict, current_user: dict) -> dict:
    request_type, from_account_id, to_account_id, amount = _validate_request_payload(
        payload,
        current_user
    )

    # Normalize empty-string account IDs to None so nullable FK columns
    # are not populated with empty strings which violate FK constraints.
    if from_account_id == "" or from_account_id is None:
        from_account_id = None
    if to_account_id == "" or to_account_id is None:
        to_account_id = None

    with SessionLocal() as session:
        branch_id = None
        destination_branch_id = None

        if request_type == TransactionType.DEPOSIT.value:
            account = session.get(AccountORM, to_account_id)
            if not account:
                raise ValueError("Destination account not found")
            branch_id = account.branch_id
            if "CUSTOMER" in current_user.get("roles", []):
                user_email = current_user.get("email")
                customer = session.execute(
                    select(CustomerORM).where(CustomerORM.email == user_email)
                ).scalar_one_or_none()
                if not customer or customer.id != account.owner_id:
                    raise ValueError("Customers may only request deposits to their own accounts")

        elif request_type == TransactionType.WITHDRAWAL.value:
            account = session.get(AccountORM, from_account_id)
            if not account:
                raise ValueError("Source account not found")
            branch_id = account.branch_id
            if "CUSTOMER" in current_user.get("roles", []):
                user_email = current_user.get("email")
                customer = session.execute(
                    select(CustomerORM).where(CustomerORM.email == user_email)
                ).scalar_one_or_none()
                if not customer or customer.id != account.owner_id:
                    raise ValueError("Customers may only request withdrawals from their own accounts")

        else:
            from_account = session.get(AccountORM, from_account_id)
            to_account = session.get(AccountORM, to_account_id)
            if not from_account:
                raise ValueError("Source account not found")
            if not to_account:
                raise ValueError("Destination account not found")
            branch_id = from_account.branch_id
            destination_branch_id = to_account.branch_id
            if "CUSTOMER" in current_user.get("roles", []):
                user_email = current_user.get("email")
                customer = session.execute(
                    select(CustomerORM).where(CustomerORM.email == user_email)
                ).scalar_one_or_none()
                if not customer or customer.id != from_account.owner_id:
                    raise ValueError("Customers may only request transfers from their own accounts")

        # Enforce branch membership only for branch staff (TELLER/BRANCH_MANAGER),
        # not for `CUSTOMER` users who create requests for their own accounts.
        roles = current_user.get("roles", [])
        if "ADMIN" not in roles and "CUSTOMER" not in roles:
            user_branch = current_user.get("branch_id")
            if not user_branch:
                raise ValueError("Branch staff must have a branch assigned")
            if branch_id != user_branch and destination_branch_id != user_branch:
                raise ValueError("Requests must be created within your own branch")

        request = TransactionRequestORM(
            id=generate_id(),
            request_type=request_type,
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=amount,
            status=RequestStatus.PENDING.value,
            requested_by=current_user.get("sub"),
            branch_id=branch_id,
            destination_branch_id=destination_branch_id,
        )

        session.add(request)
        session.flush()

        transaction = TransactionORM(
            id=generate_id(),
            request_id=request.id,
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=amount,
            type=request_type,
            status=TransactionStatus.PENDING.value,
            timestamp=datetime.utcnow(),
        )

        session.add(transaction)
        request.transaction_id = transaction.id
        session.add(request)
        session.commit()
        session.refresh(request)

        return _transaction_request_to_dict(request)


def _apply_transaction_request(request_obj, session):
    if request_obj.status != RequestStatus.PENDING.value:
        raise ValueError("Only pending requests can be approved")

    transaction = session.execute(
        select(TransactionORM).where(TransactionORM.request_id == request_obj.id)
    ).scalar_one_or_none()

    if request_obj.request_type == TransactionType.DEPOSIT.value:
        account = session.get(AccountORM, request_obj.to_account_id)
        if not account:
            raise ValueError("Destination account not found")
        if not account.active:
            raise ValueError("Destination account is inactive")
        account.balance += request_obj.amount
        if transaction is None:
            transaction = TransactionORM(
                id=generate_id(),
                request_id=request_obj.id,
                from_account_id=None,
                to_account_id=account.id,
                amount=request_obj.amount,
                type=TransactionType.DEPOSIT.value,
                status=TransactionStatus.COMPLETED.value,
                timestamp=datetime.utcnow(),
            )
            session.add(transaction)
        else:
            transaction.status = TransactionStatus.COMPLETED.value

    elif request_obj.request_type == TransactionType.WITHDRAWAL.value:
        account = session.get(AccountORM, request_obj.from_account_id)
        if not account:
            raise ValueError("Source account not found")
        if not account.active:
            raise ValueError("Source account is inactive")
        if account.balance < request_obj.amount:
            raise ValueError("Insufficient funds")
        account.balance -= request_obj.amount
        if transaction is None:
            transaction = TransactionORM(
                id=generate_id(),
                request_id=request_obj.id,
                from_account_id=account.id,
                to_account_id=None,
                amount=request_obj.amount,
                type=TransactionType.WITHDRAWAL.value,
                status=TransactionStatus.COMPLETED.value,
                timestamp=datetime.utcnow(),
            )
            session.add(transaction)
        else:
            transaction.status = TransactionStatus.COMPLETED.value

    else:
        from_account = session.get(AccountORM, request_obj.from_account_id)
        to_account = session.get(AccountORM, request_obj.to_account_id)
        if not from_account:
            raise ValueError("Source account not found")
        if not to_account:
            raise ValueError("Destination account not found")
        if not from_account.active:
            raise ValueError("Source account is inactive")
        if not to_account.active:
            raise ValueError("Destination account is inactive")
        if from_account.balance < request_obj.amount:
            raise ValueError("Insufficient funds")
        from_account.balance -= request_obj.amount
        to_account.balance += request_obj.amount
        if transaction is None:
            transaction = TransactionORM(
                id=generate_id(),
                request_id=request_obj.id,
                from_account_id=from_account.id,
                to_account_id=to_account.id,
                amount=request_obj.amount,
                type=TransactionType.TRANSFER.value,
                status=TransactionStatus.COMPLETED.value,
                timestamp=datetime.utcnow(),
            )
            session.add(transaction)
        else:
            transaction.status = TransactionStatus.COMPLETED.value

    session.add(transaction)
    request_obj.status = RequestStatus.APPROVED.value
    session.add(request_obj)


def approve_transaction_request(request_id: str, current_user: dict) -> dict:
    with SessionLocal() as session:
        request = session.get(TransactionRequestORM, request_id)
        if not request:
            raise ValueError("Request not found")

        # Branch staff may only approve requests visible to their branch.
        # ADMIN users can approve any request across branches.
        if "ADMIN" not in current_user.get("roles", []):
            user_branch = current_user.get("branch_id")
            if not user_branch:
                raise ValueError("Branch staff must have a branch assigned")
            if request.branch_id != user_branch and request.destination_branch_id != user_branch:
                raise ValueError("Cannot approve requests outside your branch")

        _apply_transaction_request(request, session)
        session.commit()
        session.refresh(request)

        return _transaction_request_to_dict(request)


def reject_transaction_request(request_id: str, current_user: dict) -> dict:
    with SessionLocal() as session:
        request = session.get(TransactionRequestORM, request_id)
        if not request:
            raise ValueError("Request not found")

        if request.status != RequestStatus.PENDING.value:
            raise ValueError("Only pending requests can be rejected")

        if "ADMIN" not in current_user.get("roles", []):
            user_branch = current_user.get("branch_id")
            if not user_branch:
                raise ValueError("Branch staff must have a branch assigned")
            if request.branch_id != user_branch and request.destination_branch_id != user_branch:
                raise ValueError("Cannot reject requests outside your branch")

        request.status = RequestStatus.REJECTED.value

        transaction = None
        if request.transaction_id:
            transaction = session.get(TransactionORM, request.transaction_id)
        else:
            transaction = session.execute(
                select(TransactionORM).where(TransactionORM.request_id == request.id)
            ).scalar_one_or_none()

        if transaction is not None:
            transaction.status = TransactionStatus.REJECTED.value
            session.add(transaction)

        session.add(request)
        session.commit()
        session.refresh(request)

        return _transaction_request_to_dict(request)


# Retrieve transactions, with optional filtering by date or transaction type.
def get_transactions(start_date=None, transaction_type=None) -> list:

    with SessionLocal() as session:
        stmt = select(TransactionORM)

        # Filter transactions by their transaction type when provided.
        if transaction_type:
            stmt = stmt.where(TransactionORM.type == transaction_type)

        # Filter transactions to only those occurring on or after the provided date.
        if start_date:
            if isinstance(start_date, str):
                try:
                    dt = datetime.strptime(start_date, "%Y-%m-%d")
                    stmt = stmt.where(TransactionORM.timestamp >= dt)

                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid date format. Use YYYY-MM-DD."
                    )

        transactions = session.scalars(stmt).all()

        # Convert database transaction objects into response dictionaries.
        return [
            {
                "id": txn.id,
                "request_id": txn.request_id,
                "from_account_id": txn.from_account_id,
                "to_account_id": txn.to_account_id,
                "amount": txn.amount,
                "type": txn.type,
                "status": txn.status,
                "timestamp": txn.timestamp,
            }
            for txn in transactions
        ]


# Deposit money into an existing customer's account.
def deposit_money(payload: dict, current_user: dict) -> dict:

    account_id = payload.get("account_id")
    amount = float(payload.get("amount", 0))

    # Deposits must be greater than zero.
    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Deposit amount must be greater than 0"
        )

    with SessionLocal() as session:
        # Find the account receiving the deposit.
        account = session.get(AccountORM, account_id)

        if not account:
            raise HTTPException(
                status_code=404,
                detail="Account not found"
            )

        # Prevent transactions against inactive accounts.
        if account.active is False:
            raise HTTPException(
                status_code=400,
                detail="Account is inactive"
            )

        # Staff members cannot interact with accounts outside their assigned branch.
        if current_user.get("branch_id") is not None and current_user.get("branch_id") != account.branch_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot interact with an account outside your branch"
            )

        # Add the deposited amount to the account balance.
        account.balance += amount

        # Create a transaction record for the deposit.
        transaction = TransactionORM(
            id=generate_id(),
            from_account_id=None,
            to_account_id=account_id,
            amount=amount,
            type=TransactionType.DEPOSIT.value,
            status=TransactionStatus.COMPLETED.value,
            timestamp=datetime.utcnow()
        )

        session.add(transaction)
        session.commit()
        session.refresh(transaction)

        # Return the newly created transaction.
        return {
            "id": transaction.id,
            "request_id": transaction.request_id,
            "from_account_id": transaction.from_account_id,
            "to_account_id": transaction.to_account_id,
            "amount": transaction.amount,
            "type": transaction.type,
            "status": transaction.status,
            "timestamp": transaction.timestamp,
        }


# Withdraw money from an existing customer's account.
def withdraw_money(payload: dict, current_user: dict) -> dict:

    account_id = payload.get("account_id")
    amount = float(payload.get("amount", 0))

    # Withdrawals must be greater than zero.
    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Withdrawal amount must be greater than 0"
        )

    with SessionLocal() as session:
        # Find the account being used for the withdrawal.
        account = session.get(AccountORM, account_id)

        if not account:
            raise HTTPException(
                status_code=404,
                detail="Account not found"
            )

        # Prevent transactions against inactive accounts.
        if account.active is False:
            raise HTTPException(
                status_code=400,
                detail="Account is inactive"
            )

        # Staff members cannot interact with accounts outside their assigned branch.
        if current_user.get("branch_id") is not None and current_user.get("branch_id") != account.branch_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot interact with an account outside your branch"
            )

        # Make sure the account has enough funds for the withdrawal.
        if account.balance < amount:
            raise HTTPException(
                status_code=400,
                detail="Insufficient funds"
            )

        # Subtract the withdrawal amount from the account balance.
        account.balance -= amount

        # Create a transaction record for the withdrawal.
        transaction = TransactionORM(
            id=generate_id(),
            from_account_id=account_id,
            to_account_id=None,
            amount=amount,
            type=TransactionType.WITHDRAWAL.value,
            status=TransactionStatus.COMPLETED.value,
            timestamp=datetime.utcnow()
        )

        session.add(transaction)
        session.commit()
        session.refresh(transaction)

        # Return the newly created transaction.
        return {
            "id": transaction.id,
            "request_id": transaction.request_id,
            "from_account_id": transaction.from_account_id,
            "to_account_id": transaction.to_account_id,
            "amount": transaction.amount,
            "type": transaction.type,
            "status": transaction.status,
            "timestamp": transaction.timestamp,
        }


# Convert a monetary amount between two different currencies.
def _convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    # Define a hardcoded dictionary of fixed exchange rates.
    fx_rates = {
        "USD": {"USD": 1.0, "EUR": 0.92, "GBP": 0.79, "JPY": 157.0},
        "EUR": {"USD": 1.09, "EUR": 1.0, "GBP": 0.86, "JPY": 170.0},
        "GBP": {"USD": 1.27, "EUR": 1.16, "GBP": 1.0, "JPY": 198.0},
        "JPY": {"USD": 0.0064, "EUR": 0.0059, "GBP": 0.0051, "JPY": 1.0},
    }

    # Normalize the input currencies to uppercase, defaulting to USD if missing.
    normalized_from = (from_currency or "USD").upper()
    normalized_to = (to_currency or "USD").upper()

    # If the source and target currencies are identical, no conversion is needed.
    if normalized_from == normalized_to:
        return amount

    # Validate that the requested conversion route exists in the rate table.
    if normalized_from not in fx_rates or normalized_to not in fx_rates[normalized_from]:
        raise HTTPException(
            status_code=400,
            detail=f"Currency conversion is not supported for {normalized_from} to {normalized_to}"
        )

    # Calculate the converted amount and round it to two decimal places for standard currency formatting.
    return round(amount * fx_rates[normalized_from][normalized_to], 2)


# Transfer money from one account to another.
def transfer_money(payload: dict, current_user: dict) -> dict:

    from_account_id = payload.get("from_account_id")
    to_account_id = payload.get("to_account_id")
    amount = float(payload.get("amount", 0))

    # Transfers must be greater than zero.
    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Transfer amount must be greater than 0"
        )

    # Prevent transferring money from an account back into itself.
    if from_account_id == to_account_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot transfer money to the same account"
        )

    with SessionLocal() as session:
        # Retrieve the account sending the money.
        from_account = session.get(AccountORM, from_account_id)

        if not from_account:
            raise HTTPException(
                status_code=404,
                detail="Sender account not found"
            )

        # Staff members cannot transfer from accounts outside their assigned branch.
        if current_user.get("branch_id") is not None and current_user.get("branch_id") != from_account.branch_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot transfer from an account outside your branch"
            )

        # CUSTOMER can only transfer from their own account.
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

            # Account.owner_id refers to Customer.id, not User.id.
            if from_account.owner_id != customer.id:
                raise HTTPException(
                    status_code=403,
                    detail="You can only transfer from your own account"
                )

        # Retrieve the account receiving the money.
        to_account = session.get(AccountORM, to_account_id)

        if not to_account:
            raise HTTPException(
                status_code=404,
                detail="Recipient account not found"
            )

        # Both accounts must be active before a transfer can occur.
        if from_account.active is False:
            raise HTTPException(
                status_code=400,
                detail="Sender account is inactive"
            )

        if to_account.active is False:
            raise HTTPException(
                status_code=400,
                detail="Recipient account is inactive"
            )

        # Make sure the sender has enough funds.
        if from_account.balance < amount:
            raise HTTPException(
                status_code=400,
                detail="Insufficient funds"
            )

        received_amount = amount
        source_currency = (from_account.currency or "USD").upper()
        target_currency = (to_account.currency or "USD").upper()

        if source_currency != target_currency:
            received_amount = _convert_currency(amount, source_currency, target_currency)

        # Move the money between the two account balances.
        from_account.balance -= amount
        to_account.balance += received_amount

        # Generate a unique ID for the transfer transaction.
        new_id = generate_id()

        # Create a record documenting the transfer.
        transaction_record = TransactionORM(
            id=new_id,
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            amount=amount,
            currency=source_currency,
            converted_amount=received_amount if source_currency != target_currency else None,
            converted_currency=target_currency if source_currency != target_currency else None,
            type=TransactionType.TRANSFER.value,
            status=TransactionStatus.COMPLETED.value,
            timestamp=datetime.utcnow(),
        )

        session.add(transaction_record)
        session.commit()
        session.refresh(transaction_record)

        # Return the completed transfer transaction.
        return {
            "id": transaction_record.id,
            "request_id": transaction_record.request_id,
            "from_account_id": transaction_record.from_account_id,
            "to_account_id": transaction_record.to_account_id,
            "amount": transaction_record.amount,
            "currency": transaction_record.currency,
            "converted_amount": transaction_record.converted_amount,
            "converted_currency": transaction_record.converted_currency,
            "type": transaction_record.type,
            "status": transaction_record.status,
            "timestamp": transaction_record.timestamp,
        }