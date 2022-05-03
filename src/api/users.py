from fastapi import APIRouter, Depends, Security, status, Response

from dependencies import get_id_hasher, get_user_domain, authenticate
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
    auth: AuthenticatedUserSchema = Security(
        authenticate, scopes=["profile:read"]
    ),
    id_hasher: IDHasher = Depends(get_id_hasher),
):
    return id_hasher.encode_obj(auth.user)


@router.delete(
    "/profile",
    response_model=PublicUserSchema,
    description="Delete profile",
)
def delete_profile(
    auth: AuthenticatedUserSchema = Security(
        authenticate, scopes=["profile:edit"]
    ),
    user_domain: UserDomain = Depends(get_user_domain),
):
    user_domain.delete(auth.user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
