# backend/src/services/agent_runner.py
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
import uuid  # Import uuid

from src.worker.tasks import run_churninator_agent
from src.db.models.agent_run import AgentRun, AgentRunCreate
from src.db.models.user import User
from src.utils.favicon import (
    get_domain_from_url,
    get_favicon_url,
)


async def queue_agent_run(
    db: AsyncSession,
    run_in: AgentRunCreate,
    owner_id: uuid.UUID,  # <-- FIX: Accept UUID
) -> AgentRun:
    """
    Creates an AgentRun record, generates its favicon_url, increments the
    user's run_count, and queues the background task.
    """
    domain = get_domain_from_url(run_in.target_url)
    favicon_url = get_favicon_url(domain)

    user_result = await db.exec(select(User).where(User.id == owner_id))
    user = user_result.one_or_none()
    if not user:
        raise ValueError("User not found")

    user.run_count += 1
    db.add(user)

    db_run_data = run_in.model_dump()
    db_run_data["owner_id"] = owner_id
    db_run_data["favicon_url"] = favicon_url

    db_run = AgentRun.model_validate(db_run_data)

    db.add(db_run)
    await db.commit()
    await db.refresh(db_run)

    run_churninator_agent.send(str(db_run.id), db_run.target_url, db_run.task_prompt)

    return db_run
