# backend/tests/worker/test_tasks.py
import pytest
from unittest.mock import AsyncMock

from src.worker import tasks
from src.services.vlm.base import VLMResponse

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_playwright_page(mocker):
    """Mocks the Playwright Page object and its methods."""
    mock_page = AsyncMock()
    mock_page.viewport_size = {"width": 1280, "height": 720}
    mock_page.mouse.click = AsyncMock()
    mock_page.keyboard.type = AsyncMock()
    mock_page.mouse.wheel = AsyncMock()
    return mock_page


async def test_execute_action_click(mock_playwright_page):
    """Test that 'click' action calculates and calls Playwright correctly."""
    action_str = "click(x=0.5, y=0.5)"
    await tasks.execute_action(mock_playwright_page, action_str, "run-123")

    # Assert that click was called with correct pixel coordinates
    # 0.5 * 1280 = 640, 0.5 * 720 = 360
    mock_playwright_page.mouse.click.assert_awaited_once_with(640, 360)


async def test_execute_action_type(mock_playwright_page):
    """Test that 'type' action calls Playwright correctly."""
    action_str = "type(text='hello world')"
    await tasks.execute_action(mock_playwright_page, action_str, "run-123")
    mock_playwright_page.keyboard.type.assert_awaited_once_with("hello world", delay=50)


async def test_agent_task_async_main_loop(mocker, db_session):
    """
    Integration test for the agent's main async loop, mocking external systems.
    """
    run_id = "test-run-id"

    # 1. Mock all external dependencies
    mocker.patch("src.worker.tasks.async_playwright", new_callable=AsyncMock)
    mock_execute = mocker.patch(
        "src.worker.tasks.execute_action", new_callable=AsyncMock
    )
    mock_redis_pub = mocker.patch(
        "src.worker.tasks.redis_client.publish", new_callable=AsyncMock
    )

    # Mock the VLM to return a sequence of actions, then terminate
    mock_vlm = mocker.patch(
        "src.worker.tasks.vlm_provider.get_next_action", new_callable=AsyncMock
    )
    mock_vlm.side_effect = [
        VLMResponse(thought="Let's click.", action="click(x=0.1, y=0.1)"),
        VLMResponse(thought="Now I'll type.", action="type(text='test')"),
        VLMResponse(thought="I'm done.", action="TERMINATE('Finished')"),
    ]

    # Mock the DB status update function
    mock_update_status = mocker.patch(
        "src.worker.tasks.update_run_status", new_callable=AsyncMock
    )

    # 2. Run the task
    await tasks.agent_task_async(run_id, "https://loop.test", "Loop test")

    # 3. Assert the outcomes
    # It should have called the VLM 3 times
    assert mock_vlm.call_count == 3
    # It should have executed the 3 actions
    assert mock_execute.call_count == 3
    mock_execute.assert_any_await("click(x=0.1, y=0.1)")
    mock_execute.assert_any_await("TERMINATE('Finished')")

    # Check status updates: RUNNING at start, COMPLETED at end
    mock_update_status.assert_any_await(db_session, run_id, "RUNNING")
    mock_update_status.assert_any_await(db_session, run_id, "COMPLETED")

    # Check that the final "END" frame was published
    mock_redis_pub.assert_any_await(f"frames:{run_id}", b"END")
