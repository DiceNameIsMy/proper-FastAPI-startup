from datetime import datetime, timedelta

from sqlalchemy.orm.session import Session

from repository.models import User, VerificationCode
from schemas.user import UserToCreateSchema
from utils.hashing import get_password_hash, generate_verification_code


def get_users(
    session: Session, offset: int, limit: int, filters: dict = {}
) -> list[User]:
    parsed_filters = (getattr(User, key) == value for key, value in enumerate(filters))
    return session.query(User).filter(*parsed_filters).offset(offset).limit(limit).all()


def get_user_by_id(session: Session, user_id: int) -> User | None:
    return session.query(User).filter(User.id == user_id).first()


def get_user_by_email(session: Session, email: str) -> User | None:
    return session.query(User).filter(User.email == email).first()


def create_user(session: Session, user: UserToCreateSchema) -> User:
    user_to_create = user.dict()
    user_to_create["password"] = get_password_hash(user_to_create["password"])

    db_user = User(**user_to_create)
    session.add(db_user)
    session.commit()
    return db_user


def verify_user_by_id(session: Session, user_id: int):
    session.query(User).filter(User.id == user_id).update({"is_email_verified": True})
    session.commit()


def delete_user(session: Session, user: User) -> None:
    session.delete(user)
    session.commit()


def validate_code_is_unique(session: Session, user_id: int, code: str) -> bool:
    return (
        session.query(VerificationCode.user_id)
        .filter(VerificationCode.user_id == user_id, VerificationCode.code == code)
        .first()
        is None
    )


def get_verification_code(
    session: Session, user_id: int, code: int
) -> VerificationCode | None:
    return (
        session.query(VerificationCode)
        .filter(VerificationCode.user_id == user_id, VerificationCode.code == code)
        .first()
    )


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


def use_verification_code(session: Session, code: VerificationCode):
    user: User = code.user
    user.is_email_verified = True
    session.add(user)
    session.delete(code)
    session.commit()
    return user
