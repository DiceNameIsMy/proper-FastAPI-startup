from datetime import timedelta

from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm

from settings import settings
from dependencies import get_db_session, authenticate, get_email_server
from repository.crud.user import (
    get_user_by_email,
    create_user,
    create_verification_code,
    get_verification_code,
    use_verification_code,
)
from schemas.auth import (
    AuthenticatedUserSchema,
    TokenSchema,
    SignedUpUserSchema,
    UserVerificationCodeSchema,
)
from schemas.user import UserToCreateSchema, PublicUserSchema
from utils.authentication import create_jwt_token
from utils.hashing import verify_password
from utils.email import EmailServer
from utils import exceptions


router = APIRouter()


@router.post(
    "/signup", response_model=SignedUpUserSchema, status_code=status.HTTP_201_CREATED
)
async def signup(
    new_user: UserToCreateSchema,
    background_tasks: BackgroundTasks,
    email_server: EmailServer = Depends(get_email_server),
    session: Session = Depends(get_db_session),
):
    if get_user_by_email(session, new_user.email):
        raise HTTPException(status_code=400, detail="email-is-taken")

    created_user = create_user(session, new_user)
    expiration_timedelta = timedelta(minutes=settings.signup_token_expires_minutes)
    code = create_verification_code(session, created_user, expiration_timedelta)

    background_tasks.add_task(
        email_server.send_verification_code, created_user.email, code.code
    )
    token = create_jwt_token(
        user_id=created_user.id,
        expiration_timedelta=expiration_timedelta,
        key=settings.secret_key,
        algorithm=settings.jwt_algorithm,
        issuer="/signup",
    )
    return SignedUpUserSchema(user=created_user, token=token)


@router.post("/signup/verify", response_model=PublicUserSchema)
def signup_verify(
    verification_code: UserVerificationCodeSchema,
    auth: AuthenticatedUserSchema = Depends(authenticate),
    session: Session = Depends(get_db_session),
):
    if auth.token_payload.get("iss") != "/signup":
        raise exceptions.bad_credentials
    if auth.user.is_email_verified:
        raise HTTPException(status_code=400, detail="email-already-verified")

    code = get_verification_code(session, auth.user.id, verification_code.code)
    if not code:
        raise HTTPException(status_code=400, detail="invalid-verification-code")

    return use_verification_code(session, code)


@router.post("/login", response_model=TokenSchema, status_code=status.HTTP_200_OK)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_db_session),
):
    user = get_user_by_email(session, form_data.username)
    if (
        (user is None)
        or (user.is_email_verified is False)
        or (verify_password(form_data.password, user.password) is False)
    ):
        raise exceptions.invalid_credentials

    return TokenSchema(
        token=create_jwt_token(
            user_id=user.id,
            expiration_timedelta=settings.jwt.access_expiration,
            key=settings.secret_key,
            algorithm=settings.jwt.algorithm,
            issuer="/login",
        )
    )
