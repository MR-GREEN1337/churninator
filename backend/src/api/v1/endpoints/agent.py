# backend/src/api/v1/endpoints/agent.py
from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc  # <-- FIX: Import desc
import uuid
from typing import List
import asyncio

from backend.src.db.postgresql import get_session
from backend.src.db.models.agent_run import AgentRun, AgentRunCreate, AgentRunRead
from backend.src.db.models.user import User
from backend.src.services import agent_runner

import redis.asyncio as redis
from starlette.responses import StreamingResponse
from backend.src.core.settings import get_settings

router = APIRouter()

redis_client = redis.Redis(
    host=get_settings().REDIS_HOST,
    port=get_settings().REDIS_PORT,
    auto_close_connection_pool=False,
)


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


async def frame_generator(run_id: str):
    """
    Subscribes to a Redis Pub/Sub channel for a given run_id
    and yields JPEG frames as they are published by the worker.
    """
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(f"frames:{run_id}")

    print(f"🎥 Started streaming frames for run_id: {run_id}")

    try:
        while True:
            # Wait for a new message
            message = await pubsub.get_message(
                ignore_subscribe_messages=True, timeout=30
            )  # 30s timeout

            if message and message["type"] == "message":
                frame_bytes = message["data"]
                # Yield the frame in the multipart format required for MJPEG
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
                )

            # If the channel is closed or no message in a while, we can assume the run is over.
            # A more robust system might check the DB status.
            if message is None:
                print(f"🛑 Stopping stream for run_id: {run_id} (timeout).")
                break
    except asyncio.CancelledError:
        print(f"🛑 Stream for run_id: {run_id} cancelled by client.")
    finally:
        await pubsub.unsubscribe(f"frames:{run_id}")
        print(f"🎬 Unsubscribed from frames:{run_id}")


@router.get("/stream/{run_id}")
async def stream_agent_view(run_id: str):
    """
    This is the MJPEG streaming endpoint. The frontend's <img> tag will
    point to this URL.
    """
    return StreamingResponse(
        frame_generator(run_id), media_type="multipart/x-mixed-replace; boundary=frame"
    )
