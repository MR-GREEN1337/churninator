# backend/src/services/vlm/gemini_provider.py
import google.generativeai as genai
from PIL import Image
from backend.src.core.settings import get_settings

settings = get_settings()


class GeminiVLMProvider:
    def __init__(self):
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY must be configured.")
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(settings.GOOGLE_MODEL)

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

        response = self.model.generate_content(prompt_parts)
        return response.text


gemini_provider = GeminiVLMProvider()
