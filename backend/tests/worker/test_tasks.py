import pytest
from unittest.mock import AsyncMock

from backend.worker import tasks
from backend.src.services.vlm.base import VLMResponse

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_playwright_page(mocker):
    """Mocks the Playwright Page object and its methods."""
    mock_page = AsyncMock()
    mock_page.viewport_size = {"width": 1280, "height": 720}
    mock_page.goto = AsyncMock()
    mock_page.screenshot = AsyncMock(return_value=b"screenshot_bytes")
    mock_page.mouse.click = AsyncMock()
    mock_page.keyboard.type = AsyncMock()
    mock_page.mouse.wheel = AsyncMock()
    return mock_page


async def test_agent_task_async_main_loop(mocker, db_session):
    """Integration test for the agent's main async execution loop."""
    run_id = "test-run-id"

    # 1. Mock all external dependencies
    mocker.patch("backend.worker.tasks.async_playwright", new_callable=AsyncMock)
    mocker.patch("backend.worker.tasks.execute_action", new_callable=AsyncMock)
    mocker.patch("backend.worker.tasks.redis.Redis", new_callable=AsyncMock)

    # Mock the VLM to return a sequence of actions, then terminate
    mock_vlm = mocker.patch(
        "backend.worker.tasks.vlm_provider.get_next_action", new_callable=AsyncMock
    )
    mock_vlm.side_effect = [
        VLMResponse(
            thought="Let's click.",
            action="click(x=0.1, y=0.1)",
            observation="A button",
            friction_score=1,
        ),
        VLMResponse(
            thought="Now I'll type.",
            action="type(text='test')",
            observation="An input field",
            friction_score=0,
        ),
        VLMResponse(
            thought="I'm done.",
            action="TERMINATE('Finished')",
            observation="Final state",
            friction_score=0,
        ),
    ]

    # Mock the DB update function and the next actor in the chain
    mock_update_status = mocker.patch(
        "backend.worker.tasks.update_run_status", new_callable=AsyncMock
    )
    mock_select_keyframes = mocker.patch("backend.worker.tasks.select_keyframes.send")

    # 2. Run the task
    # We pass a mock DB instance
    mock_db = AsyncMock()
    mock_db.get_db_session.return_value.__aiter__.return_value = [db_session]

    await tasks.agent_task_logic(
        run_id, "https://loop.test", "Loop test", mock_db, AsyncMock()
    )

    # 3. Assert the outcomes
    assert mock_vlm.call_count == 3
    assert mock_update_status.call_count == 2
    mock_update_status.assert_any_await(db_session, run_id, "RUNNING")
    mock_update_status.assert_any_await(db_session, run_id, "ANALYZING")

    # Assert that the next phase (keyframe selection) was triggered
    mock_select_keyframes.assert_called_once_with(run_id)
