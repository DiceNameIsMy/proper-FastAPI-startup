from secrets import randbelow

from hashids import Hashids
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class InvalidHash(Exception):
    pass


class InvalidObjectWithID(Exception):
    pass


class IDHasher:
    def __init__(self, salt: str, min_length: int = 0):
        self.hashids = Hashids(salt, min_length=min_length)

    def encode(self, num: int) -> str:
        return self.hashids.encode(num)

    def decode(self, hash_id: str) -> int:
        try:
            return self.hashids.decode(hash_id)[0]
        except IndexError:
            raise InvalidHash()

    def encode_obj(self, obj):
        try:
            setattr(obj, "id", self.encode(getattr(obj, "id")))
            return obj
        except AttributeError:
            raise InvalidObjectWithID(f"Object {obj} does not have an `id` attribute")


def get_hashid(salt: str, min_length: int = 0) -> Hashids:
    return IDHasher(salt, min_length=min_length)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def generate_verification_code() -> int:
    """Generate a random 6-digit integer"""
    return randbelow(900000) + 100000
