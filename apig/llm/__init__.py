"""LLM provider clients and caching utilities.

APIG is provider-neutral. We implement minimal REST clients for:
- OpenAI Responses/Chat Completions compatible endpoint (OpenAI API)
- Google Gemini Generative Language API (v1beta)

These clients are intentionally lightweight to keep the benchmark harness
portable. They are **optional** at runtime; unit tests do not require
network access.
"""
