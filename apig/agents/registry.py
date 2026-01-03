from __future__ import annotations
from typing import Dict, Type
from .base import Agent
from .rule_based import RuleBasedAgent
from .naive_llm import NaiveLLMAgent

AGENTS: Dict[str, Type[Agent]] = {
    "rule": RuleBasedAgent,
    "naive": NaiveLLMAgent,
}

def get_agent(name: str) -> Agent:
    if name not in AGENTS:
        raise KeyError(f"Unknown agent: {name}. Available: {list(AGENTS)}")
    return AGENTS[name]()
