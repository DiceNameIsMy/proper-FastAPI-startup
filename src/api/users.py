from fastapi import APIRouter, Depends, status, Response

from dependencies import get_id_hasher, get_user_domain, authenticate_access_token
from domain import DomainError
from domain.user import UserDomain
from schemas.auth import AuthenticatedUserSchema
from schemas.user import PaginatedUserSchema, PublicUserSchema
import exceptions
from utils.hashing import IDHasher


router = APIRouter()


@router.get(
    "/profile",
    response_model=PublicUserSchema,
    description="Get to know yourself",
)
def get_profile(
    auth: AuthenticatedUserSchema = Depends(authenticate_access_token),
    id_hasher: IDHasher = Depends(get_id_hasher),
):
    return id_hasher.encode_obj(auth.user)


@router.get("/users", response_model=PaginatedUserSchema)
def get_users(
    page: int = 1,
    page_size: int = 30,
    active_users: bool = True,
    user_domain: UserDomain = Depends(get_user_domain),
    id_hasher: IDHasher = Depends(get_id_hasher),
):
    offset = (page - 1) * page_size
    filters = {}
    if active_users:
        filters["is_active"] = True
    users = [
        id_hasher.encode_obj(user)
        for user in user_domain.fetch(filters, offset, page_size)
    ]
    return PaginatedUserSchema(count=len(users), items=users)


@router.get("/users/{user_id}", response_model=PublicUserSchema)
def get_user_by_id(
    user_id: str,
    user_domain: UserDomain = Depends(get_user_domain),
    id_hasher: IDHasher = Depends(get_id_hasher),
):
    try:
        user = user_domain.get_by_id(id_hasher.decode(user_id))
    except DomainError:
        raise exceptions.NotFound(detail="user_not_found")

    return id_hasher.encode_obj(user)


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete user. You can only delete yourself",
)
def delete_user_by_id(
    user_id: str,
    auth: AuthenticatedUserSchema = Depends(authenticate_access_token),
    user_domain: UserDomain = Depends(get_user_domain),
    id_hasher: IDHasher = Depends(get_id_hasher),
):
    try:
        requested_user = user_domain.get_by_id(id_hasher.decode(user_id))
    except DomainError:
        raise exceptions.NotFound(detail="user_not_found")

    if requested_user.id != auth.user.id:
        raise exceptions.PermissionDenied(detail="can_not_delete_other_user")

    user_domain.delete(requested_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
