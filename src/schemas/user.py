from pydantic import validator, EmailStr

from . import ORMBaseModel


class UserInDbSchema(ORMBaseModel):
    id: int
    email: EmailStr
    password: str
    is_active: bool
    is_email_verified: bool


class PublicUserSchema(ORMBaseModel):
    id: str
    email: EmailStr
    is_email_verified: bool


class PaginatedUserSchema(ORMBaseModel):
    count: int
    items: list[PublicUserSchema]


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
