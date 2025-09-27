# backend/tests/services/test_agent_runner.py
import pytest
from sqlmodel.ext.asyncio.session import AsyncSession
from dramatiq.brokers.stub import StubBroker

from src.services import agent_runner
from src.db.models.user import User
from src.db.models.agent_run import AgentRunCreate

pytestmark = pytest.mark.asyncio


async def test_queue_agent_run_service(
    db_session: AsyncSession, test_user: User, mock_broker: StubBroker
):
    """
    Test the agent_runner service function directly.
    - Verifies DB record creation.
    - Verifies user run_count increment.
    - Verifies message dispatch.
    """
    # Arrange
    initial_run_count = test_user.run_count
    run_in = AgentRunCreate(
        target_url="https://service-test.com", task_prompt="Service test"
    )

    # --- FIX for Mypy Error ---
    # We assert that test_user.id is not None. This is logically guaranteed by our
    # test_user fixture (which commits the user to the DB), and it narrows the type
    # from `Optional[uuid.UUID]` to `uuid.UUID` for the static type checker.
    assert test_user.id is not None
    # --- END FIX ---

    # Act
    # Now, passing test_user.id is type-safe.
    db_run = await agent_runner.queue_agent_run(
        db=db_session, run_in=run_in, owner_id=test_user.id
    )

    # Assert DB state
    await db_session.refresh(test_user)
    assert test_user.run_count == initial_run_count + 1
    assert db_run.id is not None
    assert db_run.target_url == run_in.target_url

    # This check remains correct
    assert db_run.favicon_url is not None
    assert "google.com/s2/favicons" in db_run.favicon_url

    # Assert message was dispatched
    queue = mock_broker.get_queue("default")
    assert queue.qsize() == 1
    message = queue.get()
    assert message.actor_name == "run_churninator_agent"
    assert message.args == (str(db_run.id), db_run.target_url, db_run.task_prompt)
