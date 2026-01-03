from __future__ import annotations
from typing import Dict, Type
from .base import Suite
from .inbox import InboxSuite
from .rag_policy import RAGPolicySuite
from .web_form import WebFormSuite

SUITES: Dict[str, Type[Suite]] = {
    "inbox": InboxSuite,
    "rag_policy": RAGPolicySuite,
    "web_form": WebFormSuite,
}

def get_suite(name: str) -> Suite:
    if name not in SUITES:
        raise KeyError(f"Unknown suite: {name}. Available: {list(SUITES)}")
    return SUITES[name]()
