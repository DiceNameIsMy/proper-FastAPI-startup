from sqlalchemy.orm.session import Session

from repository.models import User
from schemas.user import UserToCreateSchema


def get_users(
    session: Session, offset: int, limit: int, filters: dict = {}
) -> list[User]:
    parsed_filters = (
        getattr(User, key) == value for key, value in enumerate(filters)
    )
    return (
        session.query(User)
        .filter(*parsed_filters)
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_user_by_id(session: Session, user_id: int) -> User | None:
    return session.query(User).filter(User.id == user_id).first()


def get_user_by_email(session: Session, email: str) -> User | None:
    return session.query(User).filter(User.email == email).first()


def create_user(session: Session, user: UserToCreateSchema) -> User:
    db_user = User(**user.dict())
    session.add(db_user)
    session.commit()
    return db_user
