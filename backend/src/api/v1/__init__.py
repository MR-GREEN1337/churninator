from fastapi import APIRouter

from .endpoints import agent, users, auth, billing

router = APIRouter()

router.include_router(agent.router, prefix="/agent", tags=["Agent"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(billing.router, prefix="/billing", tags=["Billing"])
