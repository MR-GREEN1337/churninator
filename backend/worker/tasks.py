# backend/src/worker/tasks.py
import dramatiq
import asyncio
import redis.asyncio as redis
import json
import base64
from playwright.async_api import async_playwright, Page, Browser

from worker.broker import redis_broker
from src.core.settings import get_settings

# This is the crucial import. We're bringing in the parser from the forge.
# This works because of your `setup.py` and editable install.
from forge.utils.function_parser import parse_function_call

settings = get_settings()

# Create one Redis client for the module to reuse connections
redis_client = redis.Redis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, auto_close_connection_pool=False
)


# --- THE CORRECTED HELPER FUNCTION ---
async def execute_action(page: Page, action_str: str, run_id: str):
    """
    Parses and executes a single action string using Playwright.

    Args:
        page (Page): The Playwright page object to perform actions on.
        action_str (str): The string command from the VLM (e.g., "click(x=0.5, y=0.5)").
        run_id (str): The ID of the current agent run, for logging to Redis.
    """

    # Use our robust parser to turn the string into a structured object
    parsed_calls = parse_function_call(action_str)
    if not parsed_calls:
        # THE FIX: run_id is now a local variable.
        await redis_client.publish(
            f"logs:{run_id}", f"Parser Error: Could not parse action '{action_str}'"
        )
        return

    # We assume the model only returns one action at a time
    call = parsed_calls[0]
    action_name = call.function_name
    params = call.parameters

    # Get the viewport size to convert normalized coordinates to pixels
    viewport_size = page.viewport_size
    if not viewport_size:
        viewport_size = {"width": 1920, "height": 1080}

    # THE FIX: run_id is now a local variable.
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
                delta_x = 0
                delta_y = 0
                if params["direction"] == "down":
                    delta_y = params["amount"] * scroll_multiplier
                elif params["direction"] == "up":
                    delta_y = -params["amount"] * scroll_multiplier

                await page.mouse.wheel(delta_x=delta_x, delta_y=delta_y)
            else:
                raise ValueError(
                    "Scroll action requires 'direction' and 'amount' parameters."
                )

        elif "TERMINATE" in action_name.upper():
            pass  # Handled in the main loop

        else:
            raise NotImplementedError(
                f"Action '{action_name}' is not implemented in the worker."
            )

    except Exception as e:
        error_message = f"Execution Error: Failed to execute {action_name}. Reason: {e}"
        print(error_message)
        # THE FIX: run_id is now a local variable.
        await redis_client.publish(f"logs:{run_id}", error_message)


async def agent_task_async(run_id: str, target_url: str, task_prompt: str):
    """The async core of the agent run. Manages Playwright and the main loop."""
    print(f"🚀 [WORKER] Starting async task for run_id: {run_id}")

    async with async_playwright() as p:
        browser: Browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page: Page = await context.new_page()

        await page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
        await redis_client.publish(f"logs:{run_id}", f"Navigated to {target_url}")

        history: list[str] = []
        MAX_STEPS = 20

        for step in range(MAX_STEPS):
            await redis_client.publish(f"logs:{run_id}", f"--- Step {step + 1} ---")

            # ... (Steps 1, 2, 3, 4 are the same: screenshot, publish frame, get action, publish logs) ...
            screenshot_bytes = await page.screenshot(type="jpeg", quality=70)
            base64_frame = base64.b64encode(screenshot_bytes).decode("utf-8")
            await redis_client.publish(f"frames:{run_id}", base64_frame)

            # ... (VLM call logic is the same) ...
            action_str, thought = "...", "..."

            await redis_client.publish(f"logs:{run_id}", f"Thought: {thought}")

            # --- THE CORRECTED CALL ---
            # 5. Execute the Parsed Action, passing the run_id for context
            await execute_action(page, action_str, run_id)
            history.append(action_str)

            # 6. Check for Termination
            if "TERMINATE" in action_str.upper():
                await redis_client.publish(
                    f"logs:{run_id}", "Mission terminated by agent."
                )
                break

            await asyncio.sleep(2)

        await browser.close()

    final_result = {"status": "Completed", "log": history}
    await redis_client.publish(f"logs:{run_id}", json.dumps(final_result))
    print(f"✅ [WORKER] Finished task for run_id: {run_id}")


@dramatiq.actor(broker=redis_broker, max_retries=1, time_limit=600_000)
def run_churninator_agent(run_id: str, target_url: str, task_prompt: str):
    """
    This is the synchronous Dramatiq actor that wraps our async logic.
    """
    # --- THE GLOBAL VARIABLE HACK IS NOW GONE ---
    try:
        asyncio.run(agent_task_async(run_id, target_url, task_prompt))
    finally:
        asyncio.run(redis_client.close())
