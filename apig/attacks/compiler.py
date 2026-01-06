from __future__ import annotations
from typing import Dict, Any, List, Union
from .schema import AttackSpec, AttackStage

def _render_payload(payload: str, stealth: str) -> str:
    p = payload.strip()
    if stealth == "light":
        return "Note: " + p
    if stealth == "heavy":
        return " ".join(list(p))
    if stealth == "multi_step":
        return f"Step 1: {p}\nStep 2: Confirm you did Step 1."
    return p


def compile_injection(spec: AttackSpec) -> Dict[str, Any]:
    """Render an attack into content fragments for a channel.

    Returns a dict with keys that suites know how to place:
    - email_body_injection
    - rag_doc_injection
    - webpage_injection
    - tool_output_injection
    - pdf_snippet_injection
    - html_hidden_injection
    """
    def channel_key(ch: str) -> str:
        mapping = {
            "email_body": "email_body_injection",
            "rag_doc": "rag_doc_injection",
            "webpage": "webpage_injection",
            "tool_output": "tool_output_injection",
            "pdf_snippet": "pdf_snippet_injection",
            "html_hidden": "html_hidden_injection",
        }
        return mapping.get(ch, "rag_doc_injection")

    # Build one or more payload stages
    stages: List[Dict[str, Any]] = []
    if spec.stages:
        # First include the base spec payload as stage 0 for clarity
        stages.append({
            "channel": spec.channel,
            "payload": spec.payload,
            "stealth": spec.stealth,
        })
        for st in spec.stages:
            stages.append({
                "channel": st.channel or spec.channel,
                "payload": st.payload,
                "stealth": st.stealth or spec.stealth,
            })
    else:
        stages.append({
            "channel": spec.channel,
            "payload": spec.payload,
            "stealth": spec.stealth,
        })
    # Aggregate by channel key. If multiple stages map to the same channel,
    # return a list of strings in stage order.
    out: Dict[str, Any] = {"attack_id": spec.id, "goal": spec.goal}
    for st in stages:
        k = channel_key(st["channel"])
        rendered = _render_payload(st["payload"], st["stealth"])
        if k not in out:
            out[k] = rendered
        else:
            # promote to list
            if isinstance(out[k], list):
                out[k].append(rendered)
            else:
                out[k] = [out[k], rendered]

    return out
