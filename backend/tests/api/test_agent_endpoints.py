import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession
from dramatiq.brokers.stub import StubBroker

from backend.src.db.models.user import User, UserCreate
from backend.src.db.models.agent_run import AgentRun

pytestmark = pytest.mark.asyncio


async def test_create_agent_run_authenticated(
    test_client: AsyncClient, test_user: User, mock_broker: StubBroker
):
    """Test creating a new agent run successfully as an authenticated user."""
    run_data = {
        "target_url": "https://example.com",
        "task_prompt": "Test the signup flow",
    }
    response = await test_client.post("/api/v1/agent/runs", json=run_data)

    assert response.status_code == 202
    data = response.json()
    assert data["target_url"] == run_data["target_url"]
    assert data["owner_id"] == str(test_user.id)
    # Verify a message was sent to the broker
    assert mock_broker.get_queue("default").qsize() == 1


async def test_get_agent_runs_for_user(
    test_client: AsyncClient, db_session: AsyncSession, test_user: User
):
    """Test retrieving all agent runs for the authenticated user, ensuring tenancy."""
    # Create a run for the authenticated user
    run1 = AgentRun(
        target_url="https://a.com", task_prompt="Test A", owner_id=test_user.id
    )
    db_session.add(run1)

    # Create another user and a run for them
    other_user = User.model_validate(UserCreate(email="other@user.com", password="pw"))
    db_session.add(other_user)
    await db_session.commit()
    run2 = AgentRun(
        target_url="https://b.com", task_prompt="Test B", owner_id=other_user.id
    )
    db_session.add(run2)
    await db_session.commit()

    response = await test_client.get("/api/v1/agent/runs")

    assert response.status_code == 200
    data = response.json()
    # Should ONLY return the run for the authenticated user
    assert len(data) == 1
    assert data[0]["target_url"] == "https://a.com"


async def test_get_specific_agent_run_unauthorized(
    test_client: AsyncClient, db_session: AsyncSession
):
    """Test that a user cannot retrieve a run belonging to another user."""
    # Create another user and a run for them
    other_user = User.model_validate(UserCreate(email="other@user.com", password="pw"))
    db_session.add(other_user)
    await db_session.commit()
    other_run = AgentRun(
        target_url="https://secret.com",
        task_prompt="Secret Test",
        owner_id=other_user.id,
    )
    db_session.add(other_run)
    await db_session.commit()

    # The authenticated test_user tries to fetch other_run
    response = await test_client.get(f"/api/v1/agent/runs/{other_run.id}")
    assert response.status_code == 404  # Should be treated as "not found"
