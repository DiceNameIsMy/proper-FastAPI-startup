from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException

from dependencies import get_db_session
from crud import user
from schemas.user import PublicUserSchema, UserToCreateSchema


router = APIRouter()


@router.post("/signup", response_model=PublicUserSchema, status_code=201)
def signup(
    new_user: UserToCreateSchema,
    session: Session = Depends(get_db_session),
):
    if user.get_user_by_email(session, new_user.email):
        raise HTTPException(
            status_code=400,
            detail="email-is-taken",
        )
    created_user = user.create_user(session, new_user)
    return created_user
