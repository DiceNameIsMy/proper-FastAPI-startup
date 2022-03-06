from datetime import timedelta

from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from settings import settings
from dependencies import get_db_session
from crud.user import get_user_by_email, create_user
from schemas.auth import TokenSchema
from schemas.user import PublicUserSchema, UserToCreateSchema
from utils.authentication import create_access_token
from utils.exceptions import invalid_credentials_exception
from utils.hashing import verify_password


router = APIRouter()


@router.post(
    "/signup", response_model=PublicUserSchema, status_code=status.HTTP_201_CREATED
)
def signup(
    new_user: UserToCreateSchema,
    session: Session = Depends(get_db_session),
):
    if get_user_by_email(session, new_user.email):
        raise HTTPException(
            status_code=400,
            detail="email-is-taken",
        )
    created_user = create_user(session, new_user)
    return created_user


@router.post("/login", response_model=TokenSchema, status_code=status.HTTP_200_OK)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_db_session),
):
    user = get_user_by_email(session, form_data.username)
    if user is None or verify_password(form_data.password, user.password) is False:
        raise invalid_credentials_exception

    expiration_timedelta = timedelta(minutes=settings.access_token_expires_minutes)
    return TokenSchema(
        token=create_access_token(
            user.id, expiration_timedelta, settings.secret_key, settings.jwt_algorithm
        )
    )
