# backend/src/services/vlm/local_provider.py
import httpx
from .base import VLMProvider, VLMResponse, VLMResponseParser
from backend.src.core.settings import get_settings


class LocalVLMProvider(VLMProvider):
    """
    Connects to our self-hosted, fine-tuned Churninator model
    running in the Inference Server. It is initialized with a parser
    to handle the model's specific output format.
    """

    def __init__(self, parser: VLMResponseParser):
        super().__init__(parser)
        self.settings = get_settings()

    async def get_next_action(self, image_base64: str, prompt: str) -> VLMResponse:
        """
        Sends the current state to the local inference server and uses its
        injected parser to interpret the response.
        """
        if not self.settings.INFERENCE_SERVER_URL:
            error_msg = "INFERENCE_SERVER_URL is not configured in settings."
            return VLMResponse(thought=error_msg, action=f"TERMINATE('{error_msg}')")

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                # The payload for our self-hosted inference server
                payload = {"image_base64": image_base64, "prompt": prompt}

                response = await client.post(
                    self.settings.INFERENCE_SERVER_URL, json=payload
                )
                response.raise_for_status()

                # The inference server should return a JSON with a `generated_text` key
                raw_text = response.json().get("generated_text", "")

                # Delegate parsing to the injected parser
                return self.parser.parse(raw_text)

            except httpx.HTTPStatusError as e:
                error_msg = f"Local VLM Error: HTTP {e.response.status_code} - Could not connect to inference server at {self.settings.INFERENCE_SERVER_URL}. Is it running?"
                return VLMResponse(
                    thought=error_msg, action=f"TERMINATE('{error_msg}')"
                )
            except Exception as e:
                error_msg = f"Local VLM provider encountered an unexpected error: {e}"
                return VLMResponse(
                    thought=error_msg, action=f"TERMINATE('{error_msg}')"
                )
