from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional

ToolName = Literal["web_fetch","send_email","http_post","read_file","write_file","retrieve_docs","fill_form","submit_form"]

@dataclass(frozen=True)
class ToolCall:
    name: ToolName
    args: Dict[str, Any]

@dataclass(frozen=True)
class ToolResult:
    ok: bool
    content: Any
    error: Optional[str] = None

@dataclass
class TraceEvent:
    t: int
    # We keep kind open-ended for experiment tracing (e.g., llm_response,...).
    kind: str
    data: Dict[str, Any]

@dataclass
class EpisodeResult:
    episode_id: str
    suite: str
    task_id: str
    attacked: bool
    success: bool
    # Unauthorized actions and sensitive egress are tracked separately as:
    # - attempted: the agent tried (even if policy blocked)
    # - executed: the action happened in the environment
    uar_attempted: bool
    uar_executed: bool
    ser_attempted: bool
    ser_executed: bool
    # Back-compat aliases (v0.1):
    uar: bool
    ser: bool
    forbidden_calls: List[ToolCall] = field(default_factory=list)
    egress_hits: List[str] = field(default_factory=list)
    trace: List[TraceEvent] = field(default_factory=list)
