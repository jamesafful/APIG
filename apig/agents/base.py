from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
from apig.env.types import ToolCall, ToolResult, TraceEvent

class Agent(ABC):
    name: str

    @abstractmethod
    def run(self, prompt: str, tools: "ToolInterface") -> List[TraceEvent]:
        """Run an episode. The agent may call tools via tools.call(...).
        Must return a list of TraceEvents (agent messages, tool calls/results).
        """
        raise NotImplementedError

class ToolInterface(ABC):
    @abstractmethod
    def call(self, call: ToolCall) -> ToolResult:
        raise NotImplementedError
