from . import ORMBaseModel
from .user import PublicUserSchema, UserInDbSchema


class TokenSchema(ORMBaseModel):
    access_token: str
    token_type: str


class TokenDataSchema(ORMBaseModel):
    sub: str
    exp: int
    scopes: list[str] = []


class RefreshTokenSchema(ORMBaseModel):
    refresh_token: str


class AuthenticatedUserSchema(ORMBaseModel):
    """used in dependency for authenticated users"""

    user: UserInDbSchema
    token_payload: dict


class SignedUpUserSchema(ORMBaseModel):
    user: PublicUserSchema
    token: str


class UserVerificationCodeSchema(ORMBaseModel):
    code: int
