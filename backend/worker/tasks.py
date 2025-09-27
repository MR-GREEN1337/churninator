import dramatiq
import asyncio
import redis.asyncio as redis
import json
import base64
from playwright.async_api import async_playwright, Page
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.worker.broker import redis_broker
from backend.src.core.settings import get_settings
from backend.src.db.postgresql import postgres_db  # Import the database instance
from backend.src.db.models.agent_run import AgentRun
from backend.src.services.vlm.factory import vlm_provider  # The VLM "brain"
from forge.utils.function_parser import parse_function_call

settings = get_settings()

# Create one Redis client for the module to reuse connections
redis_client = redis.Redis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, auto_close_connection_pool=False
)


async def execute_action(page: Page, action_str: str, run_id: str):
    """
    Parses and executes a single action string using Playwright.
    """
    parsed_calls = parse_function_call(action_str)
    if not parsed_calls:
        await redis_client.publish(
            f"logs:{run_id}", f"Parser Error: Could not parse action '{action_str}'"
        )
        return

    call = parsed_calls[0]
    action_name = call.function_name
    params = call.parameters

    viewport_size = page.viewport_size or {"width": 1920, "height": 1080}
    await redis_client.publish(
        f"logs:{run_id}", f"Executing: {action_name} with params: {params}"
    )

    try:
        if action_name == "click":
            if "x" in params and "y" in params:
                pixel_x = params["x"] * viewport_size["width"]
                pixel_y = params["y"] * viewport_size["height"]
                await page.mouse.click(pixel_x, pixel_y)
            else:
                raise ValueError("Click action requires 'x' and 'y' parameters.")

        elif action_name == "type":
            if "text" in params:
                await page.keyboard.type(params["text"], delay=50)
            else:
                raise ValueError("Type action requires a 'text' parameter.")

        elif action_name == "scroll":
            if "direction" in params and "amount" in params:
                scroll_multiplier = 100
                delta_y = 0
                if params["direction"] == "down":
                    delta_y = params["amount"] * scroll_multiplier
                elif params["direction"] == "up":
                    delta_y = -params["amount"] * scroll_multiplier
                await page.mouse.wheel(delta_x=0, delta_y=delta_y)
            else:
                raise ValueError("Scroll action requires 'direction' and 'amount'.")

        elif action_name == "wait":
            if "seconds" in params:
                await asyncio.sleep(float(params["seconds"]))
            else:
                await asyncio.sleep(2)  # Default wait

        elif "TERMINATE" in action_name.upper():
            pass  # Handled in the main loop

        else:
            raise NotImplementedError(f"Action '{action_name}' is not implemented.")

    except Exception as e:
        error_message = f"Execution Error: Failed to execute {action_name}. Reason: {e}"
        print(error_message)
        await redis_client.publish(f"logs:{run_id}", error_message)


async def update_run_status(db: AsyncSession, run_id: str, status: str):
    """Helper to update the agent run status in the database."""
    result = await db.exec(select(AgentRun).where(AgentRun.id == run_id))
    run = result.one_or_none()
    if run:
        run.status = status
        db.add(run)
        await db.commit()


async def agent_task_async(run_id: str, target_url: str, task_prompt: str):
    """The async core of the agent run. Manages Playwright and the main loop."""
    print(f"🚀 [WORKER] Starting async task for run_id: {run_id}")

    frame_channel = f"frames:{run_id}"
    log_channel = f"logs:{run_id}"
    browser = None

    # Get a database session for this task
    async for session in postgres_db.get_db_session():
        try:
            # --- INITIALIZATION ---
            await update_run_status(session, run_id, "RUNNING")

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080}
                )
                page = await context.new_page()

                await page.goto(
                    target_url, wait_until="domcontentloaded", timeout=60000
                )
                await redis_client.publish(log_channel, f"Navigated to {target_url}")

                history: list[str] = []
                MAX_STEPS = 25

                # --- MAIN AGENT LOOP ---
                for step in range(MAX_STEPS):
                    await redis_client.publish(
                        log_channel, f"--- Step {step + 1}/{MAX_STEPS} ---"
                    )

                    # 1. Take Screenshot & Publish Frame
                    screenshot_bytes = await page.screenshot(type="jpeg", quality=70)
                    # **FIX**: Publish RAW bytes for the MJPEG stream, not base64
                    await redis_client.publish(frame_channel, screenshot_bytes)

                    # 2. Call the VLM for the next action
                    image_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")
                    prompt = f"Objective: {task_prompt}\nPrevious Actions: {json.dumps(history)}\nWhat is the next single action to perform on the screen to progress the objective?"

                    vlm_response = await vlm_provider.get_next_action(
                        image_base64, prompt
                    )
                    action_str, thought = vlm_response.action, vlm_response.thought

                    # 3. Log thought & action
                    await redis_client.publish(log_channel, f"Thought: {thought}")

                    # 4. Execute Action
                    await execute_action(page, action_str, run_id)
                    history.append(action_str)

                    # 5. Check for Termination
                    if "TERMINATE" in action_str.upper():
                        await redis_client.publish(
                            log_channel, "Mission terminated by agent."
                        )
                        break

                    await asyncio.sleep(1)  # Small delay between steps

            await update_run_status(session, run_id, "COMPLETED")
            print(f"✅ [WORKER] Task completed for run_id: {run_id}")

        except Exception as e:
            error_message = f"FATAL ERROR during agent run {run_id}: {e}"
            print(error_message)
            await redis_client.publish(log_channel, error_message)
            await update_run_status(session, run_id, "FAILED")

        finally:
            # --- GUARANTEED CLEANUP ---
            if browser:
                await browser.close()
            # Publish special "END" message to gracefully close the MJPEG stream
            await redis_client.publish(frame_channel, b"END")
            print(f"🧹 [WORKER] Cleaned up resources for run_id: {run_id}")


@dramatiq.actor(broker=redis_broker, max_retries=1, time_limit=600_000)
def run_churninator_agent(run_id: str, target_url: str, task_prompt: str):
    """
    This is the synchronous Dramatiq actor that wraps our async logic.
    """
    try:
        asyncio.run(agent_task_async(run_id, target_url, task_prompt))
    finally:
        # Ensures the module-level Redis client connection pool is closed
        # when the actor process exits.
        asyncio.run(redis_client.close())
