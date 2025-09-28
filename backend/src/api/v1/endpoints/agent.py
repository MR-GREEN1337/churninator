import asyncio
import uuid
from typing import List

from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from starlette.responses import StreamingResponse, FileResponse, Response
from pathlib import Path

from backend.src.api.v1.dependencies import get_current_user
from backend.src.core.settings import get_settings
from backend.src.db.models.agent_run import AgentRun, AgentRunCreate, AgentRunRead
from backend.src.db.models.user import User
from backend.src.db.postgresql import get_session
from backend.src.services import agent_runner

import redis.asyncio as redis

router = APIRouter()
settings = get_settings()

redis_client = redis.Redis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, auto_close_connection_pool=False
)


@router.post("/runs", status_code=status.HTTP_202_ACCEPTED, response_model=AgentRunRead)
async def create_agent_run(
    run_in: AgentRunCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if not current_user.id:
        raise HTTPException(status_code=403, detail="User ID not found")
    run = await agent_runner.queue_agent_run(
        db=db, run_in=run_in, owner_id=current_user.id
    )
    return run


@router.get("/runs", response_model=List[AgentRunRead])
async def get_agent_runs(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(AgentRun)
        .where(AgentRun.owner_id == current_user.id)
        .order_by(desc(AgentRun.created_at))
    )
    return result.scalars().all()


@router.get("/runs/{run_id}", response_model=AgentRunRead)
async def get_agent_run(
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(AgentRun).where(
            AgentRun.id == run_id, AgentRun.owner_id == current_user.id
        )
    )
    db_run = result.scalar_one_or_none()
    if not db_run:
        raise HTTPException(
            status_code=404, detail="Agent run not found or access denied"
        )
    return db_run


@router.delete("/runs/{run_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent_run(
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(AgentRun).where(
            AgentRun.id == run_id, AgentRun.owner_id == current_user.id
        )
    )
    db_run = result.scalar_one_or_none()
    if not db_run:
        raise HTTPException(
            status_code=404, detail="Agent run not found or access denied"
        )
    await db.delete(db_run)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/runs/{run_id}/screenshots/{screenshot_file}")
async def get_run_screenshot(run_id: uuid.UUID, screenshot_file: str):
    if ".." in screenshot_file:
        raise HTTPException(status_code=400, detail="Invalid filename.")
    file_path = Path(f"storage/runs/{run_id}/{screenshot_file}")
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Screenshot not found.")
    return FileResponse(str(file_path))


# --- START: Robust Streaming Generators ---
async def frame_generator(run_id: str):
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(f"frames:{run_id}")
    print(f"🎥 Started MJPEG frame stream for run_id: {run_id}")
    try:
        while True:
            # Use a short timeout to periodically check for new messages
            message = await pubsub.get_message(
                ignore_subscribe_messages=True, timeout=1.0
            )
            if message and message["type"] == "message":
                frame_bytes = message["data"]
                # If the worker sends the special "END" message, we stop.
                if frame_bytes == b"END":
                    print(
                        f"🛑 Received END message. Closing MJPEG stream for run_id: {run_id}."
                    )
                    break
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
                )
            # If no message, the loop continues, keeping the connection alive.
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        print(f"🛑 MJPEG stream for run_id: {run_id} cancelled by client.")
    finally:
        await pubsub.unsubscribe(f"frames:{run_id}")
        print(f"🎬 Unsubscribed from frames:{run_id}")


@router.get("/stream/{run_id}")
async def stream_agent_view(run_id: str):
    return StreamingResponse(
        frame_generator(run_id), media_type="multipart/x-mixed-replace; boundary=frame"
    )


async def log_generator(run_id: str, request: Request):
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(f"logs:{run_id}")
    print(f"🎙️ Started SSE log stream for run_id: {run_id}")
    try:
        yield "event: connected\ndata: Connection established\n\n"
        while True:
            if await request.is_disconnected():
                print(f"🛑 SSE log stream for run_id: {run_id} disconnected by client.")
                break
            message = await pubsub.get_message(
                ignore_subscribe_messages=True, timeout=1.0
            )
            if message and message["type"] == "message":
                log_data = message["data"].decode("utf-8")
                yield f"data: {log_data}\n\n"
            # Keep the loop alive even if there are no new logs
            await asyncio.sleep(0.1)
    except asyncio.CancelledError:
        print(f"🛑 SSE log stream for run_id: {run_id} cancelled by server.")
    finally:
        await pubsub.unsubscribe(f"logs:{run_id}")
        print(f"🎬 Unsubscribed from logs:{run_id}")


@router.get("/logs/{run_id}")
async def stream_agent_logs(run_id: str, request: Request):
    return StreamingResponse(
        log_generator(run_id, request), media_type="text/event-stream"
    )


# --- END: Robust Streaming Generators ---
