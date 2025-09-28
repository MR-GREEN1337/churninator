import dramatiq
import asyncio
import redis.asyncio as redis
import json
import base64
import os
from pathlib import Path
from playwright.async_api import async_playwright, Page
from sqlmodel.ext.asyncio.session import AsyncSession
from PIL import Image

# Import the class itself, not a global instance, for task-scoped instantiation
from backend.src.db.postgresql import PostgresDatabase
from backend.worker.broker import redis_broker
from backend.src.core.settings import get_settings
from backend.src.db.models.agent_run import AgentRun, RunStep
from backend.src.services.vlm.factory import vlm_provider
from backend.src.services.vlm.gemini_provider import gemini_provider
from forge.utils.function_parser import parse_function_call

settings = get_settings()

# --- Helper Functions ---


async def execute_action(
    page: Page, action_str: str, run_id: str, redis_client: redis.Redis
):
    """Parses and executes a single action string using Playwright."""
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
                pixel_x, pixel_y = (
                    params["x"] * viewport_size["width"],
                    params["y"] * viewport_size["height"],
                )
                await page.mouse.click(pixel_x, pixel_y)
        elif action_name == "type":
            await page.keyboard.type(params.get("text", ""), delay=50)
        elif action_name == "scroll":
            direction = params.get("direction", "down")
            amount = params.get("amount", 10)
            delta_y = amount * 100 if direction == "down" else -amount * 100
            await page.mouse.wheel(delta_x=0, delta_y=delta_y)
        elif action_name == "wait":
            await asyncio.sleep(float(params.get("seconds", 2)))
        elif "TERMINATE" in action_name.upper():
            pass
        else:
            raise NotImplementedError(f"Action '{action_name}' is not implemented.")
    except Exception as e:
        error_message = f"Execution Error: Failed to execute {action_name}. Reason: {e}"
        print(error_message)
        await redis_client.publish(f"logs:{run_id}", error_message)


async def update_run_status(db: AsyncSession, run_id: str, status: str):
    """Helper to update the agent run status in the database."""
    run = await db.get(AgentRun, run_id)
    if run:
        run.status = status
        db.add(run)
        await db.commit()


# --- Core Task Logic ---


async def agent_task_logic(
    run_id: str,
    target_url: str,
    task_prompt: str,
    db: PostgresDatabase,
    redis_client: redis.Redis,
):
    print(f"🚀 [WORKER] Starting execution phase for run_id: {run_id}")
    run_storage_path = Path(f"storage/runs/{run_id}")
    run_storage_path.mkdir(parents=True, exist_ok=True)
    frame_channel, log_channel = f"frames:{run_id}", f"logs:{run_id}"
    browser = None
    structured_log: list[RunStep] = []

    SYSTEM_PROMPT = """You are a meticulous AI agent designed to navigate web applications and analyze user flows. Your task is to follow a high-level objective and decide the best single action to take at each step based on a screenshot of the page and your previous actions.

You have the following tools available:
1. `click(x: float, y: float)`: Clicks an element at the given normalized coordinates (from 0.0 to 1.0).
2. `type(text: str)`: Types the given text into the currently focused element.
3. `scroll(direction: str, amount: int)`: Scrolls the page. `direction` must be 'up' or 'down'. `amount` is the intensity.
4. `TERMINATE(summary: str)`: Ends the mission when the objective is complete or you are stuck. Provide a brief summary.

Your response MUST be in the following format, with no other text or explanation:
<think>
[Your step-by-step reasoning on what you see in the screenshot, how it relates to your previous actions, and what your next action should be to achieve the objective.]
</think>
<code>
[The single tool call you will execute, e.g., click(x=0.51, y=0.32) or type(text='example@email.com')]
</code>"""

    async for session in db.get_db_session():
        try:
            await update_run_status(session, run_id, "RUNNING")
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080}
                )
                page = await context.new_page()
                await page.goto(
                    target_url, wait_until="domcontentloaded", timeout=60000
                )
                await redis_client.publish(log_channel, f"Navigated to {target_url}")

                for step in range(25):
                    await redis_client.publish(
                        log_channel, f"--- Step {step + 1}/25 ---"
                    )
                    screenshot_bytes = await page.screenshot(type="jpeg", quality=70)
                    await redis_client.publish(frame_channel, screenshot_bytes)
                    screenshot_path = run_storage_path / f"step_{step + 1}.jpeg"
                    screenshot_path.write_bytes(screenshot_bytes)

                    image_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")

                    # --- START: THE CRITICAL STATEFUL PROMPT FIX ---
                    history_for_prompt = "\n".join(
                        [
                            f"Step {s.step}:\nThought: {s.thought}\nAction: {s.action}"
                            for s in structured_log
                        ]
                    )

                    prompt_for_vlm = (
                        f"{SYSTEM_PROMPT}\n\n"
                        f"Here is the history of your previous actions:\n"
                        f"<history>\n{history_for_prompt}\n</history>\n\n"
                        f"Your current high-level objective is: {task_prompt}\n\n"
                        f"Based on the screenshot and your history, what is the next single action to take?"
                    )
                    # --- END: THE CRITICAL STATEFUL PROMPT FIX ---

                    vlm_response = await vlm_provider.get_next_action(
                        image_base64, prompt_for_vlm
                    )
                    action_str, thought = vlm_response.action, vlm_response.thought

                    await redis_client.publish(log_channel, f"Thought: {thought}")
                    structured_log.append(
                        RunStep(
                            step=step + 1,
                            thought=thought,
                            action=action_str,
                            screenshot_path=str(screenshot_path),
                        )
                    )
                    await execute_action(page, action_str, run_id, redis_client)

                    if "TERMINATE" in action_str.upper():
                        await redis_client.publish(
                            log_channel, "Execution phase terminated by agent."
                        )
                        break
                    await asyncio.sleep(1.5)

            run = await session.get(AgentRun, run_id)
            if run:
                run.run_log = [s.model_dump() for s in structured_log]
                session.add(run)
                await session.commit()

            await update_run_status(session, run_id, "ANALYZING")
            generate_final_report.send(run_id)
            print(f"✅ [WORKER] Execution complete for {run_id}. Triggering analysis.")
        except Exception as e:
            error_message = f"FATAL ERROR during agent run {run_id}: {e}"
            print(error_message)
            await redis_client.publish(log_channel, error_message)
            await update_run_status(session, run_id, "FAILED")
        finally:
            if browser:
                await browser.close()
            await redis_client.publish(frame_channel, b"END")


async def report_generation_logic(
    run_id: str, db: PostgresDatabase, redis_client: redis.Redis
):
    """The async core of the report generation process."""
    print(f"🔬 [ANALYZER] Starting report generation for run_id: {run_id}")
    async for session in db.get_db_session():
        run = await session.get(AgentRun, run_id)
        try:
            if not run or not run.run_log:
                raise ValueError("Run log not found.")

            log_text = "Here is the log of the agent's actions and thoughts:\n---\n"
            for step in run.run_log:
                log_text += f"Step {step['step']}:\nThought: {step['thought']}\nAction: {step['action']}\n---\n"

            image_paths = [step["screenshot_path"] for step in run.run_log]
            images = [Image.open(path) for path in image_paths if os.path.exists(path)]
            if not images:
                raise ValueError("No valid screenshots found for analysis.")

            report_json_str = gemini_provider.generate_report_from_run(images, log_text)
            report_data = json.loads(
                report_json_str.strip().replace("```json", "").replace("```", "")
            )

            run.final_result = report_data
            run.status = "COMPLETED"
            session.add(run)
            await session.commit()
            print(f"✅ [ANALYZER] Successfully generated and saved report for {run_id}")
        except Exception as e:
            print(
                f"❌ [ANALYZER] FATAL ERROR during report generation for {run_id}: {e}"
            )
            if run:
                run.status = "FAILED"
                session.add(run)
                await session.commit()


# --- The Definitive Async Lifecycle Wrapper ---


async def task_lifecycle_wrapper(actor_logic, **kwargs):
    """A single async context manager for all worker tasks."""
    db_instance = PostgresDatabase()
    redis_instance = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    try:
        # Pass the newly created instances to the actual task logic.
        await actor_logic(db=db_instance, redis_client=redis_instance, **kwargs)
    finally:
        # This cleanup happens in the SAME event loop as the task, solving the error.
        print(
            f"🧹 [WORKER] Cleaning up resources for task related to run_id: {kwargs.get('run_id')}"
        )
        await db_instance.engine.dispose()
        await redis_instance.close()


# --- Simple, Synchronous Dramatiq Actors ---


@dramatiq.actor(broker=redis_broker, max_retries=1, time_limit=900_000)
def run_churninator_agent(run_id: str, target_url: str, task_prompt: str):
    """Entrypoint actor that runs the agent execution task."""
    try:
        asyncio.run(
            task_lifecycle_wrapper(
                agent_task_logic,
                run_id=run_id,
                target_url=target_url,
                task_prompt=task_prompt,
            )
        )
    except Exception as e:
        print(f"Dramatiq actor failed for run {run_id}: {e}")


@dramatiq.actor(broker=redis_broker, max_retries=1, time_limit=600_000)
def generate_final_report(run_id: str):
    """Entrypoint actor that runs the report generation task."""
    try:
        asyncio.run(task_lifecycle_wrapper(report_generation_logic, run_id=run_id))
    except Exception as e:
        print(f"Dramatiq actor failed for report generation {run_id}: {e}")
