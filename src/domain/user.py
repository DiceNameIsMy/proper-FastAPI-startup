from datetime import datetime
from pydantic import EmailStr

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError

from modules.jwt.client import JWTClient
from modules.hashid import HashidsClient
from modules.pwd import PwdClient

from schemas.auth import TokenDataSchema

from settings import settings, oauth2_scope
from repository.models import User, VerificationCode
from repository.user import UserRepository
from schemas.user import UserInDbSchema, UserToCreateSchema

from domain import ABCDomain, DomainError


class UserDomain(ABCDomain):
    model = User

    def __init__(
        self,
        id_hasher: HashidsClient,
        pwd_client: PwdClient,
        user_repository: UserRepository,
        jwt_client: JWTClient,
    ):
        super().__init__(id_hasher, pwd_client)
        self.repository = user_repository
        self.jwt_client = jwt_client

    def get_by_id(self, user_id: int) -> User:
        try:
            return self.repository.get_by_id(user_id)
        except NoResultFound:
            raise DomainError("user_not_found")

    def get_by_email(self, email: str) -> User:
        try:
            return self.repository.get_by_email(email)
        except NoResultFound:
            raise DomainError("user_not_found")

    def fetch(self, filters: dict, page: int = 0, page_size: int = 20) -> list[User]:
        offset = page * page_size
        users = self.repository.fetch(filters, offset, page_size)
        return users

    def signup(self, new_user: UserToCreateSchema) -> tuple[User, VerificationCode, str]:
        user = self.create(new_user)
        code = self.create_verification_code(user)
        token = self.make_token(
            user, "verify_email", scopes=[oauth2_scope.profile_verify.name]
        )
        return user, code, token

    def signup_by_sso_provider(
        self, provider_name: str, provider_id: str, email: EmailStr
    ) -> tuple[User, str]:
        try:
            user, _ = self.repository.create_user_by_sso_provider(
                provider_name, provider_id, email
            )
        except IntegrityError:
            raise DomainError("user_already_exists_or_linked_by_provider")

        return user, self.make_token(user, "access", settings.auth.basic_scopes)

    def create(self, user: UserToCreateSchema) -> User:
        user_to_create = user.dict()
        user_to_create["password"] = self.pwd_client.get_password_hash(
            user_to_create["password"]
        )
        try:
            return self.repository.create_user(User(**user_to_create))
        except IntegrityError:
            raise DomainError("user_already_exists")

    def update(self, user: User) -> User:
        pass

    def delete(self, user_id: int) -> None:
        self.repository.delete_user(user_id)

    def create_verification_code(self, user: User) -> VerificationCode:
        return self.repository.create_verification_code(
            user, settings.auth.verify_email_expiration
        )

    def verify_email(self, user: UserInDbSchema, code: int):
        try:
            code_obj = self.repository.get_verification_code(user.id, code)
        except NoResultFound:
            raise DomainError("verification_code_not_found")
        if code_obj.expires_at < datetime.now(tz=code_obj.expires_at.tzinfo):
            raise DomainError("expired_verification_code")

        self.repository.use_verification_code(code_obj)

    def login(
        self, email: str, password: str, scopes: list[str] = []
    ) -> tuple[User, str]:
        try:
            user = self.repository.get_by_email(email)
        except NoResultFound:
            raise DomainError("invalid_credentials")

        if (
            user.is_email_verified is False
            or self.pwd_client.verify_password(password, user.password) is False
        ):
            raise DomainError("invalid_credentials")

        return user, self.make_token(user, "access", scopes)

    def login_by_sso_provider(self, id: str, name: str, email: str) -> tuple[User, str]:
        try:
            user, _ = self.repository.get_by_sso_provider(id, name, email)
        except NoResultFound:
            raise DomainError("user_not_found")

        return user, self.make_token(user, "access", settings.auth.basic_scopes)

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
