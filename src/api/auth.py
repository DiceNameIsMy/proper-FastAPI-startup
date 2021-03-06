from loguru import logger
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Security,
    status,
    BackgroundTasks,
)
from fastapi.security import OAuth2PasswordRequestForm

from fastapi_sso.sso.google import GoogleSSO

from settings import oauth2_scope
from domain.user import UserDomain
from domain import DomainError

from modules.hashid import HashidsClient
from modules.mailsender import ABCMailSender

from dependencies import (
    authenticate,
    get_id_hasher,
    get_user_domain,
    get_google_sso,
    get_mailsender,
)
from schemas.auth import (
    AuthenticatedUserSchema,
    RefreshTokenSchema,
    TokenSchema,
    SignedUpUserSchema,
    UserVerificationCodeSchema,
)
from schemas.user import UserToCreateSchema, PublicUserSchema
import exceptions


router = APIRouter()


@router.post(
    "/signup", response_model=SignedUpUserSchema, status_code=status.HTTP_201_CREATED
)
async def signup(
    new_user: UserToCreateSchema,
    background_tasks: BackgroundTasks,
    user_domain: UserDomain = Depends(get_user_domain),
    id_hasher: HashidsClient = Depends(get_id_hasher),
    mailsender: ABCMailSender = Depends(get_mailsender),
):
    """Create user and send verification code to email"""
    try:
        created_user, code, token = user_domain.signup(new_user)
    except DomainError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="email_is_taken"
        )

    subject = "Verify your email"
    body = f"Please verify your email by entering the following code: {code.code}"
    background_tasks.add_task(mailsender.send, created_user.email, subject, body)
    logger.info(f"Sending signup code to: {created_user.email}")

    return SignedUpUserSchema(user=id_hasher.encode_obj(created_user), token=token)


@router.post("/signup/verify", response_model=PublicUserSchema)
def signup_verify(
    verification_code: UserVerificationCodeSchema,
    auth: AuthenticatedUserSchema = Security(
        authenticate, scopes=[oauth2_scope.profile_verify.name]
    ),
    user_domain: UserDomain = Depends(get_user_domain),
    id_hasher: HashidsClient = Depends(get_id_hasher),
):
    """Verify user that has not yet verified his email"""
    if auth.user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="email_already_verified"
        )
    try:
        user_domain.verify_email(auth.user, verification_code.code)
    except DomainError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid_verification_code"
        )

    logger.info(f"Verified user: {auth.user.email}")
    return id_hasher.encode_obj(auth.user)


@router.post("/login", response_model=TokenSchema)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_domain: UserDomain = Depends(get_user_domain),
):
    """Obtain JWT token to access API as authorized user"""
    try:
        _, token = user_domain.login(
            form_data.username,
            form_data.password,
            form_data.scopes,
        )
    except DomainError:
        raise exceptions.invalid_credentials

    logger.info(f"Logged in user: {form_data.username}")
    return TokenSchema(access_token=token, token_type="bearer")


@router.get("/login/google")
async def google_login(google_sso: GoogleSSO = Depends(get_google_sso)):
    """Generate login url and redirect"""
    return await google_sso.get_login_redirect()


@router.get("/login/google/callback", response_model=TokenSchema)
async def google_callback(
    request: Request,
    google_sso: GoogleSSO = Depends(get_google_sso),
    user_domain: UserDomain = Depends(get_user_domain),
):
    """Process login response from Google and return user info"""
    open_id = await google_sso.verify_and_process(request)
    try:
        _, token = user_domain.login_by_sso_provider(
            open_id.id, open_id.provider, open_id.email
        )
    except DomainError:
        try:
            _, token = user_domain.signup_by_sso_provider(
                open_id.provider, open_id.id, open_id.email
            )
        except DomainError as e:
            logger.warning(
                f"Couldn't signup `{open_id.email}`| provider `{open_id.provider}`: {e}"
            )
            raise e
    return TokenSchema(access_token=token, token_type="bearer")


@router.post("/token/refresh", response_model=TokenSchema)
def refresh_token(
    token: RefreshTokenSchema,
    user_domain: UserDomain = Depends(get_user_domain),
    id_hasher: HashidsClient = Depends(get_id_hasher),
):
    # TODO fix accepting token type & exp
    """Refresh JWT token"""
    try:
        token_data = user_domain.read_token(token.refresh_token)
    except DomainError as e:
        raise exceptions.BadRequest(str(e))

    try:
        user = user_domain.get_by_id(id_hasher.decode(token_data.sub))
    except DomainError:
        raise exceptions.BadRequest("invalid_token")

    access_token = user_domain.make_token(user, "access", token_data.scopes)
    return TokenSchema(access_token=access_token, token_type="bearer")
