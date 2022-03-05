from pydantic import validator, EmailStr

from . import ORMBaseModel


class UserInDbSchema(ORMBaseModel):
    id: int
    email: EmailStr
    password: str
    is_active: bool


class PublicUserSchema(ORMBaseModel):
    id: int
    email: EmailStr


class UserToCreateSchema(ORMBaseModel):
    email: EmailStr
    password: str

    @validator("email", pre=True)
    def validate_email(cls, value: str):
        normalized_email = value.lower()
        return normalized_email

    @validator("password")
    def validate_password_length(cls, value: str):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return value
