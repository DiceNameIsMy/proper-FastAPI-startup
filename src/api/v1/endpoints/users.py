from fastapi import APIRouter, Depends, status, Response

from dependencies import get_user_domain, authenticate_access_token
from domain import DomainError
from domain.user.user import UserDomain
from schemas.auth import AuthenticatedUserSchema
from schemas.user import PaginatedUserSchema, PublicUserSchema
import exceptions


router = APIRouter()


@router.get(
    "/profile",
    response_model=PublicUserSchema,
    description="Get to know yourself",
)
def get_profile(auth: AuthenticatedUserSchema = Depends(authenticate_access_token)):
    return auth.user


@router.get("/users", response_model=PaginatedUserSchema)
def get_users(
    page: int = 1,
    page_size: int = 30,
    active_users: bool = True,
    user_domain: UserDomain = Depends(get_user_domain),
):
    offset = (page - 1) * page_size
    filters = {}
    if active_users:
        filters["is_active"] = True
    return user_domain.fetch(filters, offset, page_size)


@router.get("/users/{user_id}", response_model=PublicUserSchema)
def get_user_by_id(
    user_id: int,
    user_domain: UserDomain = Depends(get_user_domain),
):
    try:
        return user_domain.get_by_id(user_id)
    except DomainError:
        raise exceptions.NotFound(detail="user_not_found")


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete user. You can only delete yourself",
)
def delete_user_by_id(
    user_id: int,
    auth: AuthenticatedUserSchema = Depends(authenticate_access_token),
    user_domain: UserDomain = Depends(get_user_domain),
):
    try:
        requested_user = user_domain.get_by_id(user_id)
    except DomainError:
        raise exceptions.NotFound(detail="user_not_found")

    if requested_user.id != auth.user.id:
        raise exceptions.PermissionDenied(detail="can_not_delete_other_user")

    user_domain.delete(requested_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
