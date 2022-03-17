from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from domain.user import UserDomain
from domain import DomainError

from dependencies import (
    authenticate_verify_email_token,
    get_email_server,
    get_user_domain,
)
from schemas.auth import (
    AuthenticatedUserSchema,
    TokenSchema,
    SignedUpUserSchema,
    UserVerificationCodeSchema,
)
from schemas.user import UserToCreateSchema, PublicUserSchema
from utils.email import EmailServer
import exceptions


router = APIRouter()


@router.post(
    "/signup",
    response_model=SignedUpUserSchema,
    status_code=status.HTTP_201_CREATED,
    description="Create user and send verification code to email",
)
async def signup(
    new_user: UserToCreateSchema,
    background_tasks: BackgroundTasks,
    user_domain: UserDomain = Depends(get_user_domain),
    email_server: EmailServer = Depends(get_email_server),
):

    try:
        created_user, code, token = user_domain.signup(new_user)
    except DomainError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="email_is_taken"
        )

    background_tasks.add_task(
        email_server.send_verification_code, created_user.email, code.code
    )
    return SignedUpUserSchema(user=created_user, token=token)


@router.post(
    "/signup/verify",
    response_model=PublicUserSchema,
    description="Verify user that has not yet verified his email",
)
def signup_verify(
    verification_code: UserVerificationCodeSchema,
    auth: AuthenticatedUserSchema = Depends(authenticate_verify_email_token),
    user_domain: UserDomain = Depends(get_user_domain),
):
    if auth.user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="email_already_verified"
        )
    try:
        user = user_domain.verify_email(auth.user, verification_code.code)
    except DomainError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_verification_code"
        )

    return user


@router.post(
    "/login",
    response_model=TokenSchema,
    description="Obtain JWT token to access API as authorized user",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_domain: UserDomain = Depends(get_user_domain),
):
    try:
        _, token = user_domain.login(form_data.username, form_data.password)
    except DomainError:
        raise exceptions.invalid_credentials

    return TokenSchema(token=token)
