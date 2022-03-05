from pydantic import validator, EmailStr

from . import ORMBaseModel


class AuthCredentialsSchema(ORMBaseModel):
    email: EmailStr
    password: str

    @validator("email", pre=True)
    def validate_email(cls, value: str):
        normalized_email = value.lower()
        return normalized_email


class TokenSchema(ORMBaseModel):
    token: str
    token_type: str
