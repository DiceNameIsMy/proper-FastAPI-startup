from sqlalchemy.orm.session import Session

from repository.models import User


def get_users(session: Session, offset: int, limit: int) -> list[User]:
    return session.query(User).offset(offset).limit(limit).all()
