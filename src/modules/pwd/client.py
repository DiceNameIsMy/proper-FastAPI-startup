from passlib.context import CryptContext
from passlib.exc import UnknownHashError


class PwdClient:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except UnknownHashError:
            return False

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)
