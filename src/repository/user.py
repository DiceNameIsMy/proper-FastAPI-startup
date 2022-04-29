from datetime import datetime, timedelta

from sqlalchemy.orm.session import Session

from repository.models import User, VerificationCode
from utils.hashing import generate_verification_code


def get_users(
    session: Session, offset: int, limit: int, filters: dict = {}
) -> list[User]:
    return session.query(User).filter_by(**filters).offset(offset).limit(limit).all()


def get_user_by_id(session: Session, user_id: int) -> User:
    return session.query(User).filter_by(id=user_id).one()


def get_user_by_email(session: Session, email: str) -> User:
    return session.query(User).filter_by(email=email).one()


def create_user(session: Session, user: User) -> User:
    session.add(user)
    session.commit()
    return user


def delete_user(session: Session, user_id: int) -> None:
    session.query(User).filter_by(id=user_id).delete()
    session.commit()


def get_verification_code(session: Session, user_id: int, code: int) -> VerificationCode:
    return session.query(VerificationCode).filter_by(user_id=user_id, code=code).one()


def create_verification_code(
    session: Session, user: User, expires_at: timedelta
) -> VerificationCode:
    db_code = VerificationCode(
        user_id=user.id,
        code=generate_verification_code(),
        expires_at=datetime.now() + expires_at,
    )
    session.add(db_code)
    session.commit()
    return db_code


def use_verification_code(session: Session, code: VerificationCode) -> User:
    user: User = code.user
    user.is_email_verified = True
    session.add(user)
    session.delete(code)
    session.commit()
    return user
