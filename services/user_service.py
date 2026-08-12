from sqlalchemy import select

from models.database import SessionLocal, User as UserORM


def get_all_users() -> list:
    with SessionLocal() as session:
        users = session.scalars(select(UserORM)).all()

        return [
            {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "active": user.active,
            }
            for user in users
        ]