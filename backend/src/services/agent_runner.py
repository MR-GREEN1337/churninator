from sqlmodel.ext.asyncio.session import AsyncSession
from worker.tasks import run_churninator_agent
from src.db.models.agent_run import AgentRun, AgentRunCreate


async def queue_agent_run(
    db: AsyncSession, run_in: AgentRunCreate, owner_id: str
) -> AgentRun:
    """Creates an AgentRun record and queues the background task."""

    # Create the database record, linking it to the owner
    db_run = AgentRun.model_validate(run_in, update={"owner_id": owner_id})
    db.add(db_run)
    await db.commit()
    await db.refresh(db_run)

    # Send the job to the Dramatiq worker
    run_churninator_agent.send(str(db_run.id), db_run.target_url, db_run.task_prompt)

    return db_run
