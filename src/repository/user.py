from secrets import randbelow
from datetime import datetime, timedelta

from repository.models import User, SSOAuthorization, VerificationCode

from .base import ABCReposotory


def generate_verification_code() -> int:
    """Generate a random 6-digit integer"""
    return randbelow(900000) + 100000


class UserRepository(ABCReposotory):
    def get_by_id(self, id: int) -> User:
        return self.session.query(User).filter_by(id=id).one()

    def get_by_email(self, email: str) -> User:
        return self.session.query(User).filter_by(email=email).one()

    def get_by_sso_provider(
        self, provider_name: str, provider_id: str, email: str
    ) -> tuple[User, SSOAuthorization]:
        return (
            self.session.query(User, SSOAuthorization)
            .filter(
                SSOAuthorization.provider_name == provider_name,
                SSOAuthorization.provider_id == provider_id,
                User.email == email,
                User.id == SSOAuthorization.user_id,
            )
            .one()
        )

    def fetch(self, filters: dict = {}, offset: int = 0, limit: int = 0) -> list[User]:
        return (
            self.session.query(User)
            .filter_by(**filters)
            .offset(offset)
            .limit(limit)
            .all()
        )

    def create_user(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        return user

    def create_user_by_sso_provider(
        self, provider_name: str, provider_id: str, email: str
    ) -> tuple[User, SSOAuthorization]:
        user = User(email=email, password="", is_email_verified=True)  # type: ignore
        sso_auth = SSOAuthorization(
            provider_id=provider_id, provider_name=provider_name, user=user
        )

        self.session.add(user)
        self.session.add(sso_auth)
        self.session.commit()
        return user, sso_auth

    def delete_user(self, user_id: int) -> None:
        self.session.query(User).filter_by(id=user_id).delete()
        self.session.commit()

    def get_verification_code(self, user_id: int, code: int) -> VerificationCode:
        return (
            self.session.query(VerificationCode)
            .filter_by(user_id=user_id, code=code)
            .one()
        )

    def create_verification_code(
        self, user: User, expires_at: timedelta
    ) -> VerificationCode:
        db_code = VerificationCode(
            user_id=user.id,
            code=generate_verification_code(),
            expires_at=datetime.now() + expires_at,
        )
        self.session.add(db_code)
        self.session.commit()
        return db_code

    def use_verification_code(self, code: VerificationCode) -> User:
        user: User = code.user
        user.is_email_verified = True
        self.session.add(user)
        self.session.delete(code)
        self.session.commit()
        return user
