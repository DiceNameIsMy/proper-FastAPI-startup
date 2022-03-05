from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException, status

from dependencies import get_db_session
from repository.hashing import verify_password
from crud.user import get_user_by_email, create_user
from schemas.auth import AuthCredentialsSchema, TokenSchema
from schemas.user import PublicUserSchema, UserToCreateSchema
from authentication import create_access_token


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
    credentials: AuthCredentialsSchema,
    session: Session = Depends(get_db_session),
):
    user = get_user_by_email(session, credentials.email)
    if not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="invalid-credentials",
        )

    return TokenSchema(
        token=create_access_token(user.id),
        token_type="access",
    )
