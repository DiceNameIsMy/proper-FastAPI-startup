from fastapi import APIRouter

from .endpoints import auth, users


router = APIRouter()
router.include_router(auth.router, tags=["auth"])
router.include_router(users.router, tags=["users"])
