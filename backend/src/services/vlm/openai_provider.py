# backend/src/services/vlm/openai_provider.py
from openai import AsyncOpenAI, OpenAIError
from .base import VLMProvider, VLMResponse, VLMResponseParser
from backend.src.core.settings import get_settings


class OpenAIVLMProvider(VLMProvider):
    """
    Connects to OpenAI's API to use models like GPT-4o for multimodal reasoning.
    It is initialized with a parser to handle the model's output format.
    """

    def __init__(self, parser: VLMResponseParser):
        super().__init__(parser)
        self.settings = get_settings()
        if not self.settings.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY must be set in settings to use the OpenAIVLMProvider."
            )
        self.client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)

    async def get_next_action(self, image_base64: str, prompt: str) -> VLMResponse:
        """
        Sends the current state to the OpenAI API and uses its
        injected parser to interpret the response.
        """
        try:
            # This system prompt is crucial for forcing GPT-4o into the desired output format.
            system_prompt = "You are a helpful GUI agent. First, think step-by-step about your plan inside <think> tags. Then, provide the single pyautogui-style action to perform inside <code> tags."

            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}",
                                    "detail": "high",  # Use high detail for accurate GUI analysis
                                },
                            },
                        ],
                    },
                ],
                max_tokens=300,
                temperature=0.0,  # Set to 0 for deterministic, repeatable actions
            )

            content = response.choices[0].message.content or ""

            # Delegate parsing to the injected parser
            return self.parser.parse(content)

        except OpenAIError as e:
            error_msg = f"OpenAI API Error: {e}"
            return VLMResponse(thought=error_msg, action=f"TERMINATE('{error_msg}')")
        except Exception as e:
            error_msg = f"OpenAI provider encountered an unexpected error: {e}"
            return VLMResponse(thought=error_msg, action=f"TERMINATE('{error_msg}')")
