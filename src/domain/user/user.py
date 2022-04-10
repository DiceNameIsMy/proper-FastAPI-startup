from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from settings import settings
from repository.models import User, VerificationCode
from repository.crud.user import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    get_users,
    delete_user,
    create_verification_code,
    get_verification_code,
    use_verification_code,
)
from schemas.user import UserInDbSchema, UserToCreateSchema

from domain import ABCDomain, DomainError
from utils.authentication import create_jwt_token
from utils.hashing import get_password_hash, verify_password


class UserDomain(ABCDomain):
    model = User

    def get_by_id(self, user_id: int) -> User:
        try:
            return get_user_by_id(self.session, user_id)
        except NoResultFound:
            raise DomainError("user_not_found")

    def get_by_email(self, email: str) -> User:
        try:
            return get_user_by_email(self.session, email)
        except NoResultFound:
            raise DomainError("user_not_found")

    def fetch(
        self, filters: dict, page: int = 0, page_size: int = 20
    ) -> list[User]:
        offset = page * page_size
        users = get_users(self.session, offset, page_size, filters)
        return users

    def signup(self, new_user: UserToCreateSchema) -> tuple[User, VerificationCode, str]:
        user = self.create(new_user)
        code = self.create_verification_code(user)
        token = self.make_token(user, "verify_email")
        return user, code, token

    def create(self, user: UserToCreateSchema) -> User:
        user_to_create = user.dict()
        user_to_create["password"] = get_password_hash(user_to_create["password"])
        try:
            return create_user(self.session, User(**user_to_create))
        except IntegrityError:
            raise DomainError("user_already_exists")

    def update(self, user: User) -> User:
        pass

    def delete(self, user: User) -> None:
        delete_user(self.session, user)

    def create_verification_code(self, user: User) -> VerificationCode:
        return create_verification_code(
            self.session, user, settings.jwt.verify_email_expiration
        )

    def verify_email(self, user: UserInDbSchema, code: int):
        try:
            code_obj = get_verification_code(self.session, user.id, code)
        except NoResultFound:
            raise DomainError("verification_code_not_found")
        if code_obj.expires_at < datetime.now(tz=code_obj.expires_at.tzinfo):
            raise DomainError("expired_verification_code")
        use_verification_code(self.session, code_obj)

    def login(self, email: str, password: str) -> tuple[User, str]:
        try:
            user = get_user_by_email(self.session, email)
        except NoResultFound:
            raise DomainError("invalid_credentials")

        if (
            user.is_email_verified is False
            or verify_password(password, user.password) is False
        ):
            raise DomainError("invalid_credentials")

        return user, self.make_token(user, "access")

    def make_token(self, user: User, type: str) -> str:
        try:
            expiration_timedelta = getattr(settings.jwt, f"{type}_expiration")
        except AttributeError:
            raise DomainError("invalid_token_type")

        return create_jwt_token(
            user_id=user.id,
            expiration_timedelta=expiration_timedelta,
            key=settings.secret_key,
            algorithm=settings.jwt.algorithm,
            type=type,
        )
