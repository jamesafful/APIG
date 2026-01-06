from __future__ import annotations

import os
from typing import Dict, Any, Optional

import httpx

from .base import LLMProvider, LLMRequest, LLMResponse, LLMProviderError


class GeminiClient(LLMProvider):
    """Minimal Gemini Generative Language API client via REST.

    Endpoint style (v1beta):
      https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key=...

    Authentication: supply `api_key` or set env var `GEMINI_API_KEY`.
    """

    name = "gemini"

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://generativelanguage.googleapis.com/v1beta"):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise LLMProviderError("Missing Gemini API key (set GEMINI_API_KEY or pass api_key)")
        self.base_url = base_url.rstrip("/")

    def generate(self, req: LLMRequest) -> LLMResponse:
        url = f"{self.base_url}/models/{req.model}:generateContent"
        params = {"key": self.api_key}

        # Gemini uses a slightly different schema.
        payload: Dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{req.system_prompt}\n\n{req.user_prompt}"}],
                }
            ],
            "generationConfig": {
                "temperature": req.temperature,
                "topP": req.top_p,
                "maxOutputTokens": req.max_output_tokens,
            },
        }

        try:
            with httpx.Client(timeout=req.timeout_s) as client:
                r = client.post(url, params=params, json=payload)
            if r.status_code >= 400:
                raise LLMProviderError(f"Gemini HTTP {r.status_code}: {r.text[:300]}")
            raw = r.json()
            # Extract text from first candidate
            cand = (raw.get("candidates") or [{}])[0]
            parts = ((cand.get("content") or {}).get("parts") or [])
            text = "".join([p.get("text", "") for p in parts])
            usage = raw.get("usageMetadata")
            return LLMResponse(text=text, raw=raw, usage=usage)
        except httpx.RequestError as e:
            raise LLMProviderError(f"Gemini request failed: {e}")
        except Exception as e:
            raise LLMProviderError(f"Gemini parse failed: {e}")
