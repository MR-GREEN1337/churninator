from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.postgresql import get_db_session
from src.db.models.agent_run import AgentRunCreate, AgentRunRead
from src.services import agent_runner

# This would come from your security/auth logic
# from src.api.v1.auth import get_current_user

router = APIRouter()


# Placeholder for dependency injection of the current user
async def get_current_user_placeholder():
    # In a real app, this would decode a JWT and fetch the user from the DB
    return {"id": "mock_user_id_123"}


@router.post("/run", status_code=status.HTTP_202_ACCEPTED, response_model=AgentRunRead)
async def create_agent_run(
    run_in: AgentRunCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_user_placeholder),  # Secure this endpoint
):
    """
    Endpoint to create a new agent run.
    """
    run = await agent_runner.queue_agent_run(
        db=db, run_in=run_in, owner_id=current_user["id"]
    )
    return run
