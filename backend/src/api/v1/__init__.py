from fastapi import APIRouter

from .endpoints import agent, users

router = APIRouter()

router.include_router(agent.router, prefix="/agent", tags=["Agent"])
router.include_router(users.router, prefix="/users", tags=["Users"])
