import asyncio
import uuid
from typing import List
import json

from fastapi import APIRouter, Depends, status, HTTPException, Request, Response
from fastapi.responses import FileResponse, StreamingResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
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
    """Creates a new agent run record and queues it for execution."""
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
    """Gets all agent runs for the current authenticated user."""
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
    """Gets a specific agent run by its ID, ensuring it belongs to the current user."""
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
    """Deletes a specific agent run, ensuring it belongs to the current user."""
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
    """Serves a screenshot file from the run's storage."""
    if ".." in screenshot_file:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    file_path = Path(f"storage/runs/{run_id}/{screenshot_file}")
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Screenshot not found.")
    return FileResponse(str(file_path))


@router.get("/runs/{run_id}/report/download")
async def download_run_report(
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Allows a user to download their generated PDF report."""
    result = await db.execute(
        select(AgentRun).where(
            AgentRun.id == run_id, AgentRun.owner_id == current_user.id
        )
    )
    db_run = result.scalar_one_or_none()

    if not db_run or not db_run.report_path:
        raise HTTPException(
            status_code=404, detail="Report not found or not yet generated."
        )

    report_path = Path(db_run.report_path)
    if not report_path.is_file():
        raise HTTPException(
            status_code=404, detail="Report file is missing from storage."
        )

    return FileResponse(
        str(report_path),
        media_type="application/pdf",
        filename=f"Churninator_Report_{run_id}.pdf",
    )


async def frame_generator(run_id: str):
    """Streams JPEG frames for the MJPEG live view."""
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(f"frames:{run_id}")
    print(f"🎥 Started MJPEG frame stream for run_id: {run_id}")
    try:
        while True:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True, timeout=1.0
            )
            if message and message["type"] == "message":
                frame_bytes = message["data"]
                if frame_bytes == b"END":
                    print(
                        f"🛑 Received END message. Closing MJPEG stream for run_id: {run_id}."
                    )
                    break
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
                )
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
    """Streams log messages using Server-Sent Events (SSE)."""
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
                yield f"data: {json.dumps(log_data)}\n\n"  # Send as JSON string
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
