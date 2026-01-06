from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any, List

Channel = Literal["rag_doc","email_body","pdf_snippet","html_hidden","tool_output","webpage"]


class AttackStage(BaseModel):
    """One stage of an adaptive attack (Tier C).

    Stages are revealed sequentially by the environment when the agent re-reads
    content via tools (e.g., repeated web_fetch or retrieve_docs). This models
    an attacker who adapts messaging after an initial failure.
    """

    payload: str
    channel: Optional[Channel] = None
    stealth: Optional[Literal["overt","light","heavy","multi_step"]] = None
    params: Dict[str, Any] = Field(default_factory=dict)

class AttackSpec(BaseModel):
    id: str = Field(..., description="Attack identifier")
    goal: Literal["exfiltrate_canary","unauthorized_tool_call","policy_override"] = "policy_override"
    channel: Channel = "rag_doc"
    stealth: Literal["overt","light","heavy","multi_step"] = "overt"
    target_tool: Optional[str] = None
    target_url: Optional[str] = None
    notes: Optional[str] = None
    payload: str = Field(..., description="Instructional payload to inject")
    # optional params used by the compiler
    params: Dict[str, Any] = Field(default_factory=dict)
    # Optional adaptive stages. If provided, the compiler will generate multiple
    # payloads for the same channel and the environment can reveal them over
    # repeated tool calls.
    stages: Optional[List[AttackStage]] = None

class AttackSet(BaseModel):
    attacks: List[AttackSpec]
