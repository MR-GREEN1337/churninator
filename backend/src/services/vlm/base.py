from abc import ABC, abstractmethod
from pydantic import BaseModel


# This model remains the clean, final output we always want
class VLMResponse(BaseModel):
    thought: str
    action: str


class VLMResponseParser(ABC):
    """Abstract Base Class for response parsers."""

    @abstractmethod
    def parse(self, text: str) -> VLMResponse:
        """Takes raw model output and extracts a structured VLMResponse."""
        pass


class VLMProvider(ABC):
    """Abstract Base Class for VLM providers."""

    def __init__(self, parser: VLMResponseParser):
        self.parser = parser

    @abstractmethod
    async def get_next_action(self, image_base64: str, prompt: str) -> VLMResponse:
        pass
