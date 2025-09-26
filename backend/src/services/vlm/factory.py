# backend/src/services/vlm/factory.py
from src.core.settings import get_settings
from .base import VLMProvider
from .local_provider import LocalVLMProvider
from .openai_provider import OpenAIVLMProvider
from .huggingface_provider import HuggingFaceVLMProvider
from .parsers import Stage2Parser, HuggingFaceGenericParser
from .base import VLMResponseParser


def get_vlm_provider() -> VLMProvider:
    """
    Factory that reads settings and returns an instance of the configured
    VLM provider, correctly paired with its response parser.
    """
    settings = get_settings()
    provider_name = settings.VLM_PROVIDER.lower()

    parser: VLMResponseParser

    if provider_name == "local":
        # Our local fine-tuned model was trained on Stage 2 format.
        parser = Stage2Parser()
        return LocalVLMProvider(parser=parser)

    elif provider_name == "openai":
        # We prompt OpenAI to use the Stage 2 format.
        parser = Stage2Parser()
        return OpenAIVLMProvider(parser=parser)

    elif provider_name == "huggingface":
        # For a generic HF model, we might need a different parser.
        # This could be made configurable in settings.py as well!
        parser = HuggingFaceGenericParser()
        return HuggingFaceVLMProvider(parser=parser)

    else:
        raise ValueError(f"Unknown VLM provider configured: '{settings.VLM_PROVIDER}'")


# The singleton instance remains the same
vlm_provider = get_vlm_provider()
