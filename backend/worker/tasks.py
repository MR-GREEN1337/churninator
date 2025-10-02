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

from backend.src.db.postgresql import PostgresDatabase
from backend.worker.broker import redis_broker
from backend.src.core.settings import get_settings
from backend.src.db.models.agent_run import AgentRun, RunStep, FinalReport
from backend.src.services.vlm.factory import vlm_provider
from backend.src.services.vlm.gemini_provider import gemini_provider
from forge.utils.function_parser import parse_function_call

settings = get_settings()

# --- Helper Functions ---


def load_prompt(filename: str) -> str:
    """Loads a prompt from the 'prompts' directory."""
    prompt_path = Path(__file__).parent / "prompts" / filename
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


# Load the system prompt once at the module level for efficiency
AGENT_SYSTEM_PROMPT = load_prompt("agent_system_prompt.txt")


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
    """Phase 1: The Scout. Executes the run and annotates each step using tags."""
    print(f"🚀 [SCOUT] Starting execution & annotation for run_id: {run_id}")
    run_storage_path = Path(f"storage/runs/{run_id}")
    run_storage_path.mkdir(parents=True, exist_ok=True)
    frame_channel, log_channel = f"frames:{run_id}", f"logs:{run_id}"
    browser = None
    structured_log: list[RunStep] = []

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
                    history_for_prompt = "\n".join(
                        [
                            f"Step {s.step}: Thought: {s.thought}\nAction: {s.action}"
                            for s in structured_log
                        ]
                    )

                    user_content = f"{AGENT_SYSTEM_PROMPT}\n\n**Mission History**\n<history>\n{history_for_prompt}\n</history>\n\n**Your Current Mission Objective:**\n<objective>{task_prompt}</objective>"

                    # The inference server is responsible for adding the final model-specific tokens.
                    vlm_response = await vlm_provider.get_next_action(
                        image_base64, user_content
                    )

                    await redis_client.publish(
                        log_channel, f"Thought: {vlm_response.thought}"
                    )
                    await redis_client.publish(
                        log_channel, f"Friction Score: {vlm_response.friction_score}/10"
                    )

                    structured_log.append(
                        RunStep(
                            step=step + 1,
                            thought=vlm_response.thought,
                            action=vlm_response.action,
                            screenshot_path=str(screenshot_path),
                            observation=vlm_response.observation or "",
                            friction_score=vlm_response.friction_score or 0,
                        )
                    )

                    await execute_action(
                        page, vlm_response.action, run_id, redis_client
                    )

                    if "TERMINATE" in vlm_response.action.upper():
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
            select_keyframes.send(run_id)
            print("✅ [SCOUT] Execution complete. Triggering keyframe selection.")
        except Exception as e:
            error_message = f"FATAL ERROR during agent run {run_id}: {e}"
            print(error_message)
            await redis_client.publish(log_channel, error_message)
            await update_run_status(session, run_id, "FAILED")
        finally:
            if browser:
                await browser.close()
            await redis_client.publish(frame_channel, b"END")


async def keyframe_selection_logic(
    run_id: str, db: PostgresDatabase, redis_client: redis.Redis
):
    """Phase 2: The Strategist. Selects the most important frames for analysis."""
    print(f"🎯 [STRATEGIST] Selecting keyframes for run_id: {run_id}")
    async for session in db.get_db_session():
        run = await session.get(AgentRun, run_id)
        try:
            if not run or not run.run_log:
                raise ValueError("Run log not found.")

            log = [RunStep.model_validate(s) for s in run.run_log]
            key_indices = set()

            if log:
                key_indices.add(log[0].step)
                key_indices.add(log[-1].step)

            sorted_by_friction = sorted(
                log, key=lambda s: s.friction_score, reverse=True
            )
            for step in sorted_by_friction[:3]:
                key_indices.add(step.step)

            run.keyframe_indices = sorted(list(key_indices))
            session.add(run)
            await session.commit()
            print(
                f"✅ [STRATEGIST] Selected keyframes {run.keyframe_indices} for {run_id}. Triggering JSON analysis."
            )
            generate_final_report.send(run_id)
        except Exception as e:
            print(
                f"❌ [STRATEGIST] FATAL ERROR during keyframe selection for {run_id}: {e}"
            )
            if run:
                run.status = "FAILED"
                session.add(run)
                await session.commit()


async def report_analysis_logic(
    run_id: str, db: PostgresDatabase, redis_client: redis.Redis
):
    """Phase 3, Part 1: The Analyst. Generates the structured JSON report from keyframes."""
    print(f"🔬 [ANALYST] Starting JSON report generation for run_id: {run_id}")
    async for session in db.get_db_session():
        run = await session.get(AgentRun, run_id)
        try:
            if not run or not run.run_log or not run.keyframe_indices:
                raise ValueError("Keyframes not selected.")

            key_steps = [s for s in run.run_log if s["step"] in run.keyframe_indices]
            log_text = "Log of key agent actions:\n---\n" + "\n---\n".join(
                [
                    f"Step {s['step']}:\nThought: {s['thought']}\nAction: {s['action']}"
                    for s in key_steps
                ]
            )
            image_paths = [s["screenshot_path"] for s in key_steps]
            images = [Image.open(path) for path in image_paths if os.path.exists(path)]
            if not images:
                raise ValueError("No valid screenshots found.")

            report_json_str = gemini_provider.generate_report_from_run(images, log_text)
            report_data = json.loads(
                report_json_str.strip().replace("```json", "").replace("```", "")
            )

            run.final_result = report_data
            session.add(run)
            await session.commit()
            print(
                f"✅ [ANALYST] Saved JSON report for {run_id}. Triggering PDF design."
            )
            generate_design_report.send(run_id)
        except Exception as e:
            print(f"❌ [ANALYST] FATAL ERROR during JSON analysis for {run_id}: {e}")
            if run:
                run.status = "FAILED"
                session.add(run)
                await session.commit()


async def design_report_logic(
    run_id: str, db: PostgresDatabase, redis_client: redis.Redis
):
    """Phase 3, Part 2: The Designer. Generates the final Markdown report."""
    print(f"🎨 [DESIGNER] Starting Markdown report generation for run_id: {run_id}")
    run_storage_path = Path(f"storage/runs/{run_id}")

    async for session in db.get_db_session():
        run = await session.get(AgentRun, run_id)
        if not run or not run.final_result:
            raise ValueError("Analysis report must be generated first.")
        try:
            analysis_data = FinalReport.model_validate(run.final_result)
            image_pairs = []

            for i, point in enumerate(analysis_data.friction_points):
                before_image_path = Path(point.screenshot_path)
                after_image_path = run_storage_path / f"after_{point.step}.png"
                if before_image_path.exists():
                    before_image = Image.open(before_image_path)
                    after_image = gemini_provider.generate_improved_design(
                        before_image, point.recommendation
                    )
                    after_image.save(after_image_path)
                    image_pairs.append(
                        (
                            # Pass relative paths for Markdown images
                            str(before_image_path.name),
                            str(after_image_path.name),
                        )
                    )

            # Generate the Markdown document string
            markdown_doc_str = gemini_provider.author_markdown_report(
                analysis=analysis_data,
                target_url=run.target_url,
                task_prompt=run.task_prompt,
                image_pairs=image_pairs,
            )

            # Save the Markdown file
            md_file_path = run_storage_path / "report.md"
            md_file_path.write_text(markdown_doc_str, encoding="utf-8")

            if md_file_path.exists():
                run.report_path = str(md_file_path)
                run.status = "COMPLETED"
                session.add(run)
                await session.commit()
                print(
                    f"✅ [DESIGNER] Successfully generated Markdown report at {md_file_path}"
                )
            else:
                raise Exception("Markdown file not found after generation.")
        except Exception as e:
            print(
                f"❌ [DESIGNER] FATAL ERROR during Markdown generation for {run_id}: {e}"
            )
            if run:
                run.status = "FAILED"
                session.add(run)
                await session.commit()


# --- Async Lifecycle Wrapper ---
async def task_lifecycle_wrapper(actor_logic, **kwargs):
    """A single async context manager for all worker tasks."""
    db_instance = PostgresDatabase()
    redis_instance = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
    try:
        await actor_logic(db=db_instance, redis_client=redis_instance, **kwargs)
    finally:
        print(
            f"🧹 [WORKER] Cleaning up resources for task related to run_id: {kwargs.get('run_id')}"
        )
        await db_instance.engine.dispose()
        await redis_instance.close()


# --- Dramatiq Actors ---
@dramatiq.actor(broker=redis_broker, max_retries=1, time_limit=900_000)
def run_churninator_agent(run_id: str, target_url: str, task_prompt: str):
    """Entrypoint actor that runs the agent execution task."""
    asyncio.run(
        task_lifecycle_wrapper(
            agent_task_logic,
            run_id=run_id,
            target_url=target_url,
            task_prompt=task_prompt,
        )
    )


@dramatiq.actor(broker=redis_broker, max_retries=1)
def select_keyframes(run_id: str):
    """New actor for Phase 2."""
    asyncio.run(task_lifecycle_wrapper(keyframe_selection_logic, run_id=run_id))


@dramatiq.actor(broker=redis_broker, max_retries=1, time_limit=600_000)
def generate_final_report(run_id: str):
    """Actor for Phase 3, Part 1 (JSON Analysis)."""
    asyncio.run(task_lifecycle_wrapper(report_analysis_logic, run_id=run_id))


@dramatiq.actor(broker=redis_broker, max_retries=1, time_limit=1800_000)
def generate_design_report(run_id: str):
    """Actor for Phase 3, Part 2 (PDF Generation)."""
    asyncio.run(task_lifecycle_wrapper(design_report_logic, run_id=run_id))
