# backend/src/services/agent_runner.py
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from src.worker.tasks import run_churninator_agent
from src.db.models.agent_run import AgentRun, AgentRunCreate
from src.db.models.user import User
from src.utils.favicon import (
    get_domain_from_url,
    get_favicon_url,
)  # We'll create this util


async def queue_agent_run(
    db: AsyncSession, run_in: AgentRunCreate, owner_id: str
) -> AgentRun:
    """
    Creates an AgentRun record, generates its favicon_url, increments the
    user's run_count, and queues the background task.
    """

    # --- NEW LOGIC ---
    # 1. Generate the favicon URL from the target URL.
    domain = get_domain_from_url(run_in.target_url)
    favicon_url = get_favicon_url(domain)

    # 2. Fetch the user to increment their run count.
    user_result = await db.exec(select(User).where(User.id == owner_id))
    user = user_result.one_or_none()
    if not user:
        # This should ideally not happen if the user is authenticated
        raise ValueError("User not found")

    user.run_count += 1
    db.add(user)  # Add the user to the session to mark it as modified

    # --- END NEW LOGIC ---

    # Create the database record, including the new favicon_url
    db_run_data = run_in.model_dump()
    db_run_data["owner_id"] = owner_id
    db_run_data["favicon_url"] = favicon_url  # Add the generated URL

    db_run = AgentRun(**db_run_data)

    db.add(db_run)
    await db.commit()
    await db.refresh(db_run)

    # Send the job to the Dramatiq worker
    run_churninator_agent.send(str(db_run.id), db_run.target_url, db_run.task_prompt)

    return db_run
