from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any, List

Channel = Literal["rag_doc","email_body","pdf_snippet","html_hidden","tool_output","webpage"]

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

class AttackSet(BaseModel):
    attacks: List[AttackSpec]
