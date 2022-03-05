from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends
from pydantic import parse_obj_as

from dependencies import get_db_session
from crud import user
from schemas.user import UserSchema


router = APIRouter()


@router.get("/")
def get_users(
    page: int = 1,
    page_size: int = 30,
    session: Session = Depends(get_db_session),
):
    offset = (page - 1) * page_size
    return parse_obj_as(
        list[UserSchema], user.get_users(session, offset, page_size)
    )
