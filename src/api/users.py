from fastapi import APIRouter, Depends, Security, status, Response

from dependencies import get_id_hasher, get_user_domain, authenticate
from domain import DomainError
from domain.user import UserDomain
from modules.hashid import HashidsClient
from schemas.auth import AuthenticatedUserSchema
from schemas.user import PaginatedUserSchema, PublicUserSchema
from settings import oauth2_scope
import exceptions


router = APIRouter()


@router.get("/profile", response_model=PublicUserSchema)
def get_profile(
    auth: AuthenticatedUserSchema = Security(
        authenticate, scopes=[oauth2_scope.profile_read.name]
    ),
    id_hasher: HashidsClient = Depends(get_id_hasher),
):
    """Get to know yourself"""
    return id_hasher.encode_obj(auth.user)


@router.delete("/profile", response_model=PublicUserSchema)
def delete_profile(
    auth: AuthenticatedUserSchema = Security(
        authenticate, scopes=[oauth2_scope.profile_edit.name]
    ),
    user_domain: UserDomain = Depends(get_user_domain),
):
    """Delete profile"""
    user_domain.delete(auth.user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/users", response_model=PaginatedUserSchema)
def get_users(
    page: int = 1,
    page_size: int = 30,
    active_users: bool = True,
    user_domain: UserDomain = Depends(get_user_domain),
    id_hasher: HashidsClient = Depends(get_id_hasher),
):
    """Get users. Only active users retrieved by default"""
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
    id_hasher: HashidsClient = Depends(get_id_hasher),
):
    try:
        user = user_domain.get_by_id(id_hasher.decode(user_id))
    except DomainError:
        raise exceptions.NotFound(detail="user_not_found")

    return id_hasher.encode_obj(user)
