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

from domain.user.user_exceptions import (
    UserDomainError,
    UserNotFoundError,
    UserAlreadyExistError,
)
from domain import ABCDomain
from utils.authentication import create_jwt_token
from utils.hashing import get_password_hash


class UserDomain(ABCDomain):
    def get_user_by_id(self, user_id: int) -> User:
        user = get_user_by_id(self.session, user_id)
        if not user:
            raise UserNotFoundError()
        return user

    def get_user_by_email(self, email: str) -> User:
        user = get_user_by_email(self.session, email)
        if not user:
            raise UserNotFoundError()
        return user

    def fetch_users(
        self, filters: dict, page: int = 0, page_size: int = 20
    ) -> PaginatedUserSchema:
        offset = page * page_size
        users = get_users(self.session, offset, page_size, filters)
        return PaginatedUserSchema(
            count=len(users), items=parse_obj_as(list[UserInDbSchema], users)
        )

    def signup_user(
        self, new_user: UserToCreateSchema
    ) -> tuple[User, VerificationCode, str]:
        user = self.create_user(new_user)
        code = self.create_verification_code(user)
        token = create_jwt_token(
            user_id=user.id,
            expiration_timedelta=settings.jwt.signup_expiration,
            key=settings.secret_key,
            algorithm=settings.jwt.algorithm,
            issuer="/signup",
        )
        return user, code, token

    def create_user(self, user: UserToCreateSchema) -> User:
        user_to_create = user.dict()
        user_to_create["password"] = get_password_hash(user_to_create["password"])

        db_user = User(**user_to_create)
        self.session.add(db_user)
        try:
            self.session.commit()
        except IntegrityError:
            raise UserAlreadyExistError()
        return db_user

    def update_user(self, user: User) -> User:
        pass

    def delete_user(self, user_id: int) -> None:
        delete_user(self.session, user_id)

    def create_verification_code(self, user: User) -> VerificationCode:
        return create_verification_code(
            self.session, user, settings.jwt.signup_expiration
        )

    def verify_user(self, user: UserInDbSchema, code: int) -> User:
        if user.is_email_verified:
            raise UserDomainError("email-already-verified")

        code_obj = get_verification_code(self.session, user.id, code)
        if code_obj is None:
            raise UserDomainError("invalid-verification-code")
        if code_obj.expires_at < datetime.now():
            raise UserDomainError("invalid-verification-code")

        return use_verification_code(self.session, code)
