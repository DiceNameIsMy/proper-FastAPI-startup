from fastapi import APIRouter, Depends, status, Response

from dependencies import get_user_domain, authenticate_access_token
from domain import DomainError
from domain.user.user import UserDomain
from schemas.auth import AuthenticatedUserSchema
from schemas.user import PaginatedUserSchema, PublicUserSchema
from utils import exceptions


router = APIRouter()


@router.get("/profile", response_model=PublicUserSchema)
def get_profile(auth: AuthenticatedUserSchema = Depends(authenticate_access_token)):
    return auth.user


@router.get("/users", response_model=PaginatedUserSchema)
def get_users(
    page: int = 1,
    page_size: int = 30,
    user_domain: UserDomain = Depends(get_user_domain),
):
    offset = (page - 1) * page_size
    return user_domain.fetch({"is_active": True}, offset, page_size)


@router.get("/users/{user_id}", response_model=PublicUserSchema)
def get_user_by_id(
    user_id: int,
    user_domain: UserDomain = Depends(get_user_domain),
):
    try:
        return user_domain.get_by_id(user_id)
    except DomainError as e:
        raise exceptions.NotFound(detail=str(e))


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_by_id(
    user_id: int,
    auth: AuthenticatedUserSchema = Depends(authenticate_access_token),
    user_domain: UserDomain = Depends(get_user_domain),
):
    try:
        requested_user = user_domain.get_by_id(user_id)
    except DomainError as e:
        raise exceptions.NotFound(detail=str(e))

    if requested_user.id != auth.user.id:
        raise exceptions.PermissionDenied(detail="can-not-delete-other-user")

    user_domain.delete(requested_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
