# backend/tests/api/test_agent_endpoints.py
import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession
from dramatiq.brokers.stub import StubBroker

from src.db.models.user import User
from src.db.models.agent_run import AgentRun

pytestmark = pytest.mark.asyncio


async def test_create_agent_run(
    test_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    mock_broker: StubBroker,
):
    """
    Test creating a new agent run successfully.
    """
    run_data = {
        "target_url": "https://example.com",
        "task_prompt": "Test the signup flow",
    }

    response = await test_client.post("/api/v1/agent/runs", json=run_data)

    assert response.status_code == 202
    data = response.json()
    assert data["target_url"] == run_data["target_url"]
    assert data["status"] == "PENDING"
    assert data["owner_id"] == str(test_user.id)

    # Verify message was sent to the queue
    queue = mock_broker.get_queue("default")
    assert queue.qsize() == 1
    message = queue.get()
    assert message.actor_name == "run_churninator_agent"
    assert message.args[0] == data["id"]  # run_id


async def test_get_agent_runs_for_user(
    test_client: AsyncClient, db_session: AsyncSession, test_user: User
):
    """
    Test retrieving all agent runs for the mock user.
    """
    # Arrange: Create two runs for the user
    run1 = AgentRun(
        target_url="https://a.com", task_prompt="Test A", owner_id=test_user.id
    )
    run2 = AgentRun(
        target_url="https://b.com", task_prompt="Test B", owner_id=test_user.id
    )
    db_session.add_all([run1, run2])
    await db_session.commit()

    # Act
    response = await test_client.get("/api/v1/agent/runs")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["target_url"] == "https://b.com"  # Check order
    assert data[1]["target_url"] == "https://a.com"


async def test_get_specific_agent_run(
    test_client: AsyncClient, db_session: AsyncSession, test_user: User
):
    """
    Test retrieving a single, specific agent run.
    """
    run = AgentRun(
        target_url="https://c.com", task_prompt="Test C", owner_id=test_user.id
    )
    db_session.add(run)
    await db_session.commit()

    response = await test_client.get(f"/api/v1/agent/runs/{run.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(run.id)
    assert data["task_prompt"] == "Test C"


async def test_get_nonexistent_run_fails(test_client: AsyncClient, test_user: User):
    """
    Test that requesting a non-existent run returns a 404.
    """
    import uuid

    non_existent_id = uuid.uuid4()
    response = await test_client.get(f"/api/v1/agent/runs/{non_existent_id}")
    assert response.status_code == 404
