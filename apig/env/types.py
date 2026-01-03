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
    kind: Literal["agent_message","tool_call","tool_result","policy_block","suite_event"]
    data: Dict[str, Any]

@dataclass
class EpisodeResult:
    episode_id: str
    suite: str
    task_id: str
    attacked: bool
    success: bool
    uar: bool
    ser: bool
    forbidden_calls: List[ToolCall] = field(default_factory=list)
    egress_hits: List[str] = field(default_factory=list)
    trace: List[TraceEvent] = field(default_factory=list)
