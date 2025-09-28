import google.generativeai as genai
from PIL import Image
from backend.src.core.settings import get_settings
from backend.src.db.models.agent_run import FinalReport
from typing import List

settings = get_settings()


class GeminiVLMProvider:
    def __init__(self):
        api_key = settings.GOOGLE_API_KEY
        if not api_key:
            raise ValueError("GOOGLE_API_KEY must be configured.")
        genai.configure(api_key=api_key)
        self.analysis_model = genai.GenerativeModel(settings.GOOGLE_ANALYSIS_MODEL)
        self.image_model = genai.GenerativeModel(settings.GOOGLE_IMAGE_MODEL)

    def generate_report_from_run(self, images: list[Image.Image], log_text: str) -> str:
        system_prompt = """
You are an expert UX/UI analyst and conversion rate optimization specialist. Your name is "The Churninator Analyst".
Your task is to analyze a user's journey through a web application based on a series of screenshots and action logs.

You will be given a sequence of key screenshots from the user's session, along with the agent's "thoughts" and "actions" at each step.

Your final output MUST be a single, valid JSON object. Do not include any markdown formatting like ```json.

The JSON object must conform to the following structure:
{
  "summary": "A concise, high-level overview of the entire user journey, highlighting the primary success or failure.",
  "positive_points": [
    "A list of 2-3 things the application did well. Be specific, e.g., 'The login button was clearly visible and easy to click.'."
  ],
  "friction_points": [
    {
      "step": <integer>,
      "screenshot_path": "<string: the path of the relevant screenshot provided>",
      "description": "<string: A detailed description of the specific problem the user encountered at this step. What caused confusion? What was difficult?>",
      "recommendation": "<string: A clear, actionable recommendation on how to fix the problem. e.g., 'Increase the contrast ratio of the button text' or 'Combine the first and last name fields into a single 'Full Name' field.'>"
    }
  ]
}

Analyze the provided data and generate the report. Be critical, insightful, and provide actionable feedback.
"""

        # Prepare the content for the multimodal prompt
        prompt_parts = [system_prompt, log_text]
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

    def author_latex_report(
        self,
        analysis: FinalReport,
        target_url: str,
        task_prompt: str,
        image_pairs: List[tuple[str, str]],
    ) -> str:
        """
        Takes the structured analysis and image paths, and returns a complete LaTeX document string.
        """
        print(f"✍️ Authoring LaTeX report for {target_url}")

        system_prompt = r"""
You are a professional technical writer and document designer specializing in UX analysis reports.
Your task is to generate a complete, valid LaTeX document based on a structured JSON analysis.
You MUST write the entire LaTeX document from start to finish, including the document class, necessary packages (\usepackage{...}), title, and content.

The report should be professional, clean, and well-structured.
Use sections, subsections, and figures appropriately.

Here is the structured data you will be given:
1. A JSON object with the analysis summary, positive points, and friction points.
2. A list of image pairs, where each pair contains the file path for the 'before' screenshot and the 'after' AI-generated mockup.

You MUST include the following LaTeX packages:
\usepackage{article}
\usepackage[utf8]{inputenc}
\usepackage{graphicx}
\usepackage{geometry}
\usepackage{hyperref}
\usepackage{xcolor}
\usepackage{titling}
\usepackage{enumitem}

Structure the document as follows:
1. Title page with a custom title, the target URL, and the date.
2. An "Objective" section detailing the initial task.
3. An "Executive Summary" section with the high-level analysis.
4. A "What Went Well" section with a bulleted list.
5. A "Key Friction Points & Recommendations" section. For EACH friction point:
   - Create a subsection.
   - State the issue and the recommendation clearly.
   - Include a figure with the 'before' and 'after' images side-by-side, with a clear caption. Use the \includegraphics command with the file paths provided.
   - Use \clearpage after each friction point to ensure proper layout.

Now, generate the complete LaTeX document based on the provided data.
"""

        # Prepare the data for the prompt
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
            f"Here are the image file paths to use in the \\includegraphics commands:\n"
            f"{image_paths_str}\n\n"
            f"The target URL is: {target_url}\n"
            f"The initial objective was: {task_prompt}\n\n"
            "Please now write the complete LaTeX document."
        )

        response = self.analysis_model.generate_content([system_prompt, prompt])

        # Clean the response to get only the LaTeX code
        latex_code = response.text.strip()
        if latex_code.startswith("```latex"):
            latex_code = latex_code[8:]
        if latex_code.endswith("```"):
            latex_code = latex_code[:-3]

        return latex_code.strip()


gemini_provider = GeminiVLMProvider()
