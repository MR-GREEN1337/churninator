# backend/src/api/v1/endpoints/agent.py
from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc  # <-- FIX: Import desc
import uuid
from typing import List

from src.db.postgresql import get_session
from src.db.models.agent_run import AgentRun, AgentRunCreate, AgentRunRead
from src.db.models.user import User
from src.services import agent_runner

router = APIRouter()


# MOCK DEPENDENCY
async def get_current_user_id_mock(
    db: AsyncSession = Depends(get_session),
) -> uuid.UUID:
    user_result = await db.exec(select(User).limit(1))
    user = user_result.one_or_none()
    if not user or not user.id:  # Added check for user.id
        raise HTTPException(
            status_code=404, detail="No mock user found for authentication."
        )
    return user.id


@router.post("/runs", status_code=status.HTTP_202_ACCEPTED, response_model=AgentRunRead)
async def create_agent_run(
    run_in: AgentRunCreate,
    db: AsyncSession = Depends(get_session),
    owner_id: uuid.UUID = Depends(get_current_user_id_mock),
):
    """Endpoint to create a new agent run."""
    run = await agent_runner.queue_agent_run(db=db, run_in=run_in, owner_id=owner_id)
    return run


@router.get("/runs", response_model=List[AgentRunRead])
async def get_agent_runs(
    db: AsyncSession = Depends(get_session),
    owner_id: uuid.UUID = Depends(get_current_user_id_mock),
):
    """Get all agent runs for the current user."""
    runs = await db.exec(
        select(AgentRun)
        .where(AgentRun.owner_id == owner_id)
        # --- FIX for Mypy Error 3 ---
        .order_by(desc(AgentRun.created_at))
        # --- END FIX ---
    )
    return runs.all()


@router.get("/runs/{run_id}", response_model=AgentRunRead)
async def get_agent_run(
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    owner_id: uuid.UUID = Depends(get_current_user_id_mock),
):
    """Get a specific agent run by its ID."""
    run = await db.exec(
        select(AgentRun).where(AgentRun.id == run_id, AgentRun.owner_id == owner_id)
    )
    db_run = run.one_or_none()
    if not db_run:
        raise HTTPException(status_code=404, detail="Agent run not found")
    return db_run
