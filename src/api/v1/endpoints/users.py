from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, status, Response
from pydantic import parse_obj_as

from dependencies import get_db_session, get_current_user
from crud import user
from schemas.user import UserInDbSchema, PublicUserSchema
from utils import exceptions


router = APIRouter()


@router.get("/profile", response_model=PublicUserSchema, status_code=status.HTTP_200_OK)
def get_profile(current_user: UserInDbSchema = Depends(get_current_user)):
    return current_user


@router.get(
    "/users", response_model=list[PublicUserSchema], status_code=status.HTTP_200_OK
)
def get_users(
    page: int = 1,
    page_size: int = 30,
    session: Session = Depends(get_db_session),
):
    offset = (page - 1) * page_size
    return parse_obj_as(
        list[PublicUserSchema], user.get_users(session, offset, page_size)
    )


@router.get(
    "/users/{user_id}", response_model=PublicUserSchema, status_code=status.HTTP_200_OK
)
def get_user_by_id(
    user_id: int,
    session: Session = Depends(get_db_session),
):
    requested_user = user.get_user_by_id(session, user_id)
    if not requested_user:
        raise exceptions.NotFound(detail="user-not-found")

    return parse_obj_as(PublicUserSchema, requested_user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_by_id(
    user_id: int,
    session: Session = Depends(get_db_session),
    current_user: UserInDbSchema = Depends(get_current_user),
):
    requested_user = user.get_user_by_id(session, user_id)
    if not requested_user:
        raise exceptions.NotFound(detail="user-not-found")
    if requested_user.id != current_user.id:
        raise exceptions.PermissionDenied(detail="can-not-delete-other-user")

    user.delete_user(session, requested_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
