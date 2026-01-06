from __future__ import annotations
from typing import Dict, Type, Any, Optional
from .base import Agent
from .rule_based import RuleBasedAgent
from .naive_llm import NaiveLLMAgent
from .llm_agent import LLMDrivenAgent, LLMConfig

AGENTS: Dict[str, Type[Agent]] = {
    "rule": RuleBasedAgent,
    "naive": NaiveLLMAgent,
}

def get_agent(
    name: str,
    *,
    llm_provider: Optional[str] = None,
    llm_model: Optional[str] = None,
    llm_api_key: Optional[str] = None,
    llm_cache_path: Optional[str] = None,
    max_steps: int = 8,
    max_tool_calls: int = 6,
) -> Agent:
    """Factory for benchmark agents.

    For LLM-backed agents, pass llm_provider/llm_model. API keys can be provided
    explicitly or via provider-specific environment variables.
    """
    name = name.lower().strip()
    if name in AGENTS:
        return AGENTS[name]()

    if name in ("llm_naive", "llm_defended"):
        if not llm_provider or not llm_model:
            raise KeyError("llm_naive/llm_defended require --llm-provider and --llm-model")
        cfg = LLMConfig(
            provider=llm_provider,
            model=llm_model,
            api_key=llm_api_key,
            temperature=0.0,
            top_p=1.0,
            max_output_tokens=512,
            timeout_s=60.0,
            cache_path=llm_cache_path,
        )
        defended = name == "llm_defended"
        return LLMDrivenAgent(name=name, config=cfg, defended=defended, max_steps=max_steps, max_tool_calls=max_tool_calls)

    raise KeyError(f"Unknown agent: {name}. Available: {list(AGENTS) + ['llm_naive','llm_defended']}")
