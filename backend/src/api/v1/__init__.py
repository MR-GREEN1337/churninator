from fastapi import APIRouter

from .endpoints import agent

router = APIRouter()

router.include_router(agent.router, prefix="/agent", tags=["Agent"])
