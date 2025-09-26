import httpx
from .base import VLMProvider, VLMResponse, VLMResponseParser
from src.core.settings import get_settings


class HuggingFaceVLMProvider(VLMProvider):
    """
    Connects to the serverless Hugging Face Inference API to run any compatible
    vision-language model hosted on the Hub.
    """

    def __init__(self, parser: VLMResponseParser):
        super().__init__(parser)
        self.settings = get_settings()

        if not self.settings.HF_INFERENCE_API_KEY:
            raise ValueError(
                "HF_INFERENCE_API_KEY must be set in settings to use the HuggingFaceVLMProvider."
            )
        if not self.settings.HF_MODEL_ID:
            raise ValueError(
                "HF_MODEL_ID must be set in settings to specify which model to use."
            )

        self.api_url = (
            f"https://api-inference.huggingface.co/models/{self.settings.HF_MODEL_ID}"
        )
        self.headers = {"Authorization": f"Bearer {self.settings.HF_INFERENCE_API_KEY}"}

    async def get_next_action(self, image_base64: str, prompt: str) -> VLMResponse:
        """
        Sends a request to the Hugging Face Inference API and uses its
        injected parser to interpret the response.
        """
        # The payload structure for image-to-text models can vary. This is a common pattern.
        # You may need to adapt the `prompt` format depending on the specific model's requirements.
        payload = {
            "inputs": {
                "image": image_base64,
                "prompt": f"<|user|>\n<image>\n{prompt}<|end|>\n<|assistant|>",
            },
            "parameters": {"max_new_tokens": 150},
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    self.api_url, headers=self.headers, json=payload
                )

                # Handle the "model loading" state (cold start)
                if response.status_code == 503:
                    error_info = response.json()
                    estimated_time = error_info.get("estimated_time", 30)
                    wait_message = f"Model '{self.settings.HF_MODEL_ID}' is loading on Hugging Face, please wait ~{int(estimated_time)}s and retry."
                    # Returning a special thought/action allows the worker to handle this gracefully
                    return VLMResponse(
                        thought=wait_message, action=f"WAIT({int(estimated_time)})"
                    )

                response.raise_for_status()

                # The response is typically a list with one dictionary
                response_data = response.json()
                raw_text = response_data[0].get("generated_text", "")

                # Delegate parsing to the injected parser
                return self.parser.parse(raw_text)

            except httpx.HTTPStatusError as e:
                error_msg = f"Hugging Face API Error: HTTP {e.response.status_code} - {e.response.text}"
                return VLMResponse(
                    thought=error_msg, action=f"TERMINATE('{error_msg}')"
                )
            except Exception as e:
                error_msg = (
                    f"Hugging Face provider encountered an unexpected error: {e}"
                )
                return VLMResponse(
                    thought=error_msg, action=f"TERMINATE('{error_msg}')"
                )
