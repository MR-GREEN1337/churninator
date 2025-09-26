# forge/eval/eval_prompt.py

# --- AGUVIS Stage 1 (Grounding) Evaluation Prompt ---
# Tests the model's basic ability to map an instruction directly to an action.
# EXPECTS OUTPUT: "Action: click(x=..., y=...)"

SCREENSPOT_V2_USER_PROMPT_PHASE_1 = """Using the screenshot, you will get an instruction and will need to output the action that completes the instruction or targets the given element.

Just write your action as follows:

Action: click(x=0.XXXX, y=0.YYYY)
With 0.XXXX and 0.YYYY the normalized coordinates of the click position on the screenshot.

Now write the action needed to complete the instruction:
Instruction: {instruction}
"""


# --- AGUVIS Stage 2 (Reasoning) Evaluation Prompt ---
# Tests the model's ability to use the "Thought -> Action" process.
# EXPECTS OUTPUT: "<think>...</think>\n<code>click(x=..., y=...)</code>"

# The system prompt defines the rules and the tools available.
STAGE_2_SYSTEM_PROMPT = """You are a helpful GUI agent. Your goal is to complete the given instruction. First, think step-by-step about your plan inside <think> tags. Then, provide the single action to perform inside <code> tags."""

# The user prompt provides the specific task.
STAGE_2_USER_PROMPT = """Instruction: {instruction}"""
