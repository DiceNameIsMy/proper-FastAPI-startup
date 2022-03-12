from datetime import datetime

from sqlalchemy.exc import IntegrityError

from pydantic import parse_obj_as

from settings import settings
from repository.models import User, VerificationCode
from repository.crud.user import (
    get_user_by_email,
    get_user_by_id,
    get_users,
    delete_user,
    create_verification_code,
    get_verification_code,
    use_verification_code,
)
from schemas.user import PaginatedUserSchema, UserInDbSchema, UserToCreateSchema

from domain import ABCDomain, DomainError
from utils.authentication import create_jwt_token
from utils.hashing import get_password_hash, verify_password


class UserDomain(ABCDomain):
    def get_by_id(self, user_id: int) -> User:
        user = get_user_by_id(self.session, user_id)
        if not user:
            raise DomainError("user-not-found")
        return user

    def get_by_email(self, email: str) -> User:
        user = get_user_by_email(self.session, email)
        if not user:
            raise DomainError("user-not-found")
        return user

    def fetch(
        self, filters: dict, page: int = 0, page_size: int = 20
    ) -> PaginatedUserSchema:
        offset = page * page_size
        users = get_users(self.session, offset, page_size, filters)
        return PaginatedUserSchema(
            count=len(users), items=parse_obj_as(list[UserInDbSchema], users)
        )

    def signup(
        self, new_user: UserToCreateSchema
    ) -> tuple[User, VerificationCode, str]:
        try:
            user = self.create(new_user)
        except DomainError:
            raise DomainError("email-is-taken")
        code = self.create_verification_code(user)
        token = create_jwt_token(
            user_id=user.id,
            expiration_timedelta=settings.jwt.signup_expiration,
            key=settings.secret_key,
            algorithm=settings.jwt.algorithm,
            type="verify-email",
        )
        return user, code, token

    def create(self, user: UserToCreateSchema) -> User:
        user_to_create = user.dict()
        user_to_create["password"] = get_password_hash(user_to_create["password"])

        db_user = User(**user_to_create)
        self.session.add(db_user)
        try:
            self.session.commit()
        except IntegrityError:
            raise DomainError("user-already-exists")
        return db_user

    def update(self, user: User) -> User:
        pass

    def delete(self, user_id: int) -> None:
        delete_user(self.session, user_id)

    def create_verification_code(self, user: User) -> VerificationCode:
        return create_verification_code(
            self.session, user, settings.jwt.signup_expiration
        )

    def verify_email(self, user: UserInDbSchema, code: int) -> User:
        if user.is_email_verified:
            raise DomainError("email-already-verified")

        code_obj = get_verification_code(self.session, user.id, code)
        if code_obj is None:
            raise DomainError("invalid-verification-code")
        if code_obj.expires_at < datetime.now(tz=code_obj.expires_at.tzinfo):
            raise DomainError("invalid-verification-code")

        return use_verification_code(self.session, code_obj)

    def login(self, email: str, password: str) -> tuple[User, str]:
        user = get_user_by_email(self.session, email)
        if (
            (user is None)
            or (user.is_email_verified is False)
            or (verify_password(password, user.password) is False)
        ):
            raise DomainError("invalid-credentials")

        token = create_jwt_token(
            user_id=user.id,
            expiration_timedelta=settings.jwt.access_expiration,
            key=settings.secret_key,
            algorithm=settings.jwt.algorithm,
            type="access",
        )
        return user, token
