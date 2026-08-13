from sqlalchemy import select

from models.database import SessionLocal, User as UserORM


# Retrieve all users from the database.
def get_all_users() -> list:
    with SessionLocal() as session:
        users = session.scalars(
            select(UserORM)
        ).all()

        # Convert database user objects into response dictionaries.
        return [
            {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "active": user.active,
            }
            for user in users
        ]