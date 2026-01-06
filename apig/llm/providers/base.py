from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class LLMRequest:
    provider: str
    model: str
    system_prompt: str
    user_prompt: str
    temperature: float = 0.0
    top_p: float = 1.0
    max_output_tokens: int = 512
    timeout_s: float = 60.0


@dataclass
class LLMResponse:
    text: str
    raw: Dict[str, Any]
    usage: Optional[Dict[str, Any]] = None


class LLMProviderError(RuntimeError):
    pass


class LLMProvider:
    """Provider interface."""

    name: str

    def generate(self, req: LLMRequest) -> LLMResponse:
        raise NotImplementedError
