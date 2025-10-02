import google.generativeai as genai
from PIL import Image
from backend.src.core.settings import get_settings
from backend.src.db.models.agent_run import FinalReport
from typing import List
from pathlib import Path

settings = get_settings()


def load_prompt(filename: str) -> str:
    """Loads a prompt from the 'prompts' directory."""
    prompt_path = (
        Path(__file__).parent.parent.parent.parent / "worker/prompts" / filename
    )
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


# Load prompts at the module level
REPORT_ANALYST_PROMPT = load_prompt("report_analyst_prompt.txt")
MARKDOWN_DESIGNER_PROMPT = load_prompt("markdown_designer_prompt.txt")


class GeminiVLMProvider:
    def __init__(self):
        api_key = settings.GOOGLE_API_KEY
        if not api_key:
            raise ValueError("GOOGLE_API_KEY must be configured.")
        genai.configure(api_key=api_key)
        self.analysis_model = genai.GenerativeModel(settings.GOOGLE_ANALYSIS_MODEL)
        self.image_model = genai.GenerativeModel(settings.GOOGLE_IMAGE_MODEL)

    def generate_report_from_run(self, images: list[Image.Image], log_text: str) -> str:
        # Prepare the content for the multimodal prompt
        prompt_parts = [REPORT_ANALYST_PROMPT, log_text]
        prompt_parts.extend(images)

        response = self.analysis_model.generate_content(prompt_parts)
        return response.text

    def generate_improved_design(
        self, original_image: Image.Image, recommendation: str
    ) -> Image.Image:
        print(f"🎨 Generating improved design based on: '{recommendation}'")
        prompt = (
            "You are a world-class UI/UX designer. "
            f"Using the provided screenshot of a web page, generate a new image that implements the following design recommendation: '{recommendation}'. "
            "The new image should look like a realistic, improved version of the original screenshot. "
            "Keep the overall branding and style consistent, but apply the specific change. Only output the new image."
        )
        response = self.image_model.generate_content([prompt, original_image])
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                from io import BytesIO

                return Image.open(BytesIO(part.inline_data.data))
        raise ValueError("Image generation failed to return an image.")

    def author_markdown_report(
        self,
        analysis: FinalReport,
        target_url: str,
        task_prompt: str,
        image_pairs: List[tuple[str, str]],
    ) -> str:
        """
        Takes the structured analysis and image paths, and returns a complete Markdown document string.
        """
        print(f"✍️ Authoring Markdown report for {target_url}")

        analysis_json_str = analysis.model_dump_json(indent=2)
        image_paths_str = "\n".join(
            [
                f"Pair {i+1}: Before='{pair[0]}', After='{pair[1]}'"
                for i, pair in enumerate(image_pairs)
            ]
        )

        prompt = (
            f"Here is the analysis data:\n"
            f"```json\n{analysis_json_str}\n```\n\n"
            f"Here are the image file paths to use in the Markdown image tags:\n"
            f"{image_paths_str}\n\n"
            f"The target URL is: {target_url}\n"
            f"The initial objective was: {task_prompt}\n\n"
            "Please now write the complete Markdown document."
        )

        response = self.analysis_model.generate_content(
            [MARKDOWN_DESIGNER_PROMPT, prompt]
        )

        # Clean the response to get only the Markdown code
        markdown_code = response.text.strip()
        if markdown_code.startswith("```markdown"):
            markdown_code = markdown_code[10:]
        if markdown_code.startswith("```"):
            markdown_code = markdown_code[3:]
        if markdown_code.endswith("```"):
            markdown_code = markdown_code[:-3]

        return markdown_code.strip()


gemini_provider = GeminiVLMProvider()
