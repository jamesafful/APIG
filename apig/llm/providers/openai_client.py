from __future__ import annotations

import os
from typing import Dict, Any, Optional

import httpx

from .base import LLMProvider, LLMRequest, LLMResponse, LLMProviderError


class OpenAIClient(LLMProvider):
    """Minimal OpenAI Chat Completions client via REST.

    We use the widely supported `v1/chat/completions` endpoint for maximum
    compatibility. This keeps dependencies light and makes caching deterministic.

    Authentication: supply `api_key` or set env var `OPENAI_API_KEY`.
    """

    name = "openai"

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise LLMProviderError("Missing OpenAI API key (set OPENAI_API_KEY or pass api_key)")
        self.base_url = base_url.rstrip("/")

    def generate(self, req: LLMRequest) -> LLMResponse:
        url = f"{self.base_url}/chat/completions"
        payload: Dict[str, Any] = {
            "model": req.model,
            "messages": [
                {"role": "system", "content": req.system_prompt},
                {"role": "user", "content": req.user_prompt},
            ],
            "temperature": req.temperature,
            "top_p": req.top_p,
            "max_tokens": req.max_output_tokens,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=req.timeout_s) as client:
                r = client.post(url, json=payload, headers=headers)
            if r.status_code >= 400:
                raise LLMProviderError(f"OpenAI HTTP {r.status_code}: {r.text[:300]}")
            raw = r.json()
            text = raw["choices"][0]["message"]["content"]
            usage = raw.get("usage")
            return LLMResponse(text=text, raw=raw, usage=usage)
        except httpx.RequestError as e:
            raise LLMProviderError(f"OpenAI request failed: {e}")
        except Exception as e:
            raise LLMProviderError(f"OpenAI parse failed: {e}")
