from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException
from pydantic import parse_obj_as

from dependencies import get_db_session
from crud import user
from schemas.user import PublicUserSchema


router = APIRouter()


@router.get("/users", response_model=list[PublicUserSchema], status_code=200)
def get_users(
    page: int = 1,
    page_size: int = 30,
    session: Session = Depends(get_db_session),
):
    offset = (page - 1) * page_size
    return parse_obj_as(
        list[PublicUserSchema], user.get_users(session, offset, page_size)
    )


@router.get("/users/{user_id}", response_model=PublicUserSchema, status_code=200)
def get_user_by_id(
    user_id: int,
    session: Session = Depends(get_db_session),
):
    requested_user = user.get_user_by_id(session, user_id)
    if not requested_user:
        raise HTTPException(status_code=404, detail="user-not-found")

    return parse_obj_as(PublicUserSchema, requested_user)
