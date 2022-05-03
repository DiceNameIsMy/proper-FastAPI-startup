from . import ORMBaseModel
from .user import PublicUserSchema, UserInDbSchema


class TokenSchema(ORMBaseModel):
    token: str


class TokenDataSchema(ORMBaseModel):
    sub: str
    exp: int
    scopes: list[str] = []


class AuthenticatedUserSchema(ORMBaseModel):
    """used in dependency for authenticated users"""

    user: UserInDbSchema
    token_payload: dict


class SignedUpUserSchema(ORMBaseModel):
    user: PublicUserSchema
    token: str


class UserVerificationCodeSchema(ORMBaseModel):
    code: int
