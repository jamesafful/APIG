from __future__ import annotations

from typing import Optional

from .base import LLMProvider
from .openai_client import OpenAIClient
from .gemini_client import GeminiClient


def get_provider(name: str, api_key: Optional[str] = None) -> LLMProvider:
    name = name.lower().strip()
    if name == "openai":
        return OpenAIClient(api_key=api_key)
    if name == "gemini":
        return GeminiClient(api_key=api_key)
    raise ValueError(f"Unknown provider: {name} (expected 'openai' or 'gemini')")
