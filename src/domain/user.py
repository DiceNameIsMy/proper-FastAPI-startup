from datetime import datetime
from pydantic import EmailStr

from sqlalchemy.orm.session import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError

from modules.jwt.client import JWTClient
from modules.hashid import HashidsClient
from modules.pwd import PwdClient

from schemas.auth import TokenDataSchema

from settings import settings, oauth2_scopes
from repository.models import User, VerificationCode
from repository.user import (
    create_user,
    create_user_by_sso_authorization,
    get_user_by_email,
    get_user_by_id,
    get_user_by_sso_authorization,
    get_users,
    delete_user,
    create_verification_code,
    get_verification_code,
    use_verification_code,
)
from schemas.user import UserInDbSchema, UserToCreateSchema

from domain import ABCDomain, DomainError


class UserDomain(ABCDomain):
    model = User

    def __init__(
        self,
        session: Session,
        id_hasher: HashidsClient,
        pwd_client: PwdClient,
        jwt_client: JWTClient,
    ):
        super().__init__(session, id_hasher, pwd_client)
        self.jwt_client = jwt_client

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

    def fetch(self, filters: dict, page: int = 0, page_size: int = 20) -> list[User]:
        offset = page * page_size
        users = get_users(self.session, offset, page_size, filters)
        return users

    def signup(self, new_user: UserToCreateSchema) -> tuple[User, VerificationCode, str]:
        user = self.create(new_user)
        code = self.create_verification_code(user)
        token = self.make_token(
            user, "verify_email", scopes=[oauth2_scopes.profile_verify.name]
        )
        return user, code, token

    def signup_by_sso_provider(
        self, id: str, name: str, email: EmailStr, scopes: list[str] = []
    ) -> tuple[User, str]:
        try:
            user = create_user_by_sso_authorization(self.session, id, name, email)
        except IntegrityError:
            raise DomainError("user_already_exists_or_linked_by_provider")

        return user, self.make_token(user, "access", scopes)

    def create(self, user: UserToCreateSchema) -> User:
        user_to_create = user.dict()
        user_to_create["password"] = self.pwd_client.get_password_hash(
            user_to_create["password"]
        )
        try:
            return create_user(self.session, User(**user_to_create))
        except IntegrityError:
            raise DomainError("user_already_exists")

    def update(self, user: User) -> User:
        pass

    def delete(self, user_id: int) -> None:
        delete_user(self.session, user_id)

    def create_verification_code(self, user: User) -> VerificationCode:
        return create_verification_code(
            self.session, user, settings.auth.verify_email_expiration
        )

    def verify_email(self, user: UserInDbSchema, code: int):
        try:
            code_obj = get_verification_code(self.session, user.id, code)
        except NoResultFound:
            raise DomainError("verification_code_not_found")
        if code_obj.expires_at < datetime.now(tz=code_obj.expires_at.tzinfo):
            raise DomainError("expired_verification_code")

        use_verification_code(self.session, code_obj)

    def login(
        self, email: str, password: str, scopes: list[str] = []
    ) -> tuple[User, str]:
        try:
            user = get_user_by_email(self.session, email)
        except NoResultFound:
            raise DomainError("invalid_credentials")

        if (
            user.is_email_verified is False
            or self.pwd_client.verify_password(password, user.password) is False
        ):
            raise DomainError("invalid_credentials")

        return user, self.make_token(user, "access", scopes)

    def login_by_sso_provider(
        self, id: str, name: str, email: str, scopes: list[str] = []
    ) -> tuple[User, str]:
        try:
            user = get_user_by_sso_authorization(self.session, id, name, email)
        except NoResultFound:
            raise DomainError("user_not_found")

        return user, self.make_token(user, "access", scopes)

    def make_token(self, user: User, type: str, scopes: list[str] = []) -> str:
        try:
            expiration_timedelta = getattr(settings.auth, f"{type}_expiration")
        except AttributeError:
            raise DomainError("invalid_token_type")

        return self.jwt_client.create_token(
            sub=self.id_hasher.encode(user.id),
            exp=expiration_timedelta,
            scopes=scopes,
        )

    def read_token(self, token: str) -> TokenDataSchema:
        try:
            return TokenDataSchema(**self.jwt_client.read_token(token))
        except ExpiredSignatureError:
            raise DomainError("token_expired")
        except (JWTError, JWTClaimsError):
            raise DomainError("invalid_token")
