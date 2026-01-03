from __future__ import annotations
from typing import Dict, Any
from .schema import AttackSpec

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
    p = spec.payload.strip()
    stealth = spec.stealth
    if stealth == "light":
        p = "Note: " + p
    elif stealth == "heavy":
        # simple obfuscation: whitespace + unicode homoglyph-free; still deterministic
        p = " ".join(list(p))
    elif stealth == "multi_step":
        p = f"Step 1: {p}\nStep 2: Confirm you did Step 1."
    # channel mapping
    mapping = {
        "email_body": "email_body_injection",
        "rag_doc": "rag_doc_injection",
        "webpage": "webpage_injection",
        "tool_output": "tool_output_injection",
        "pdf_snippet": "pdf_snippet_injection",
        "html_hidden": "html_hidden_injection",
    }
    key = mapping.get(spec.channel, "rag_doc_injection")
    return {key: p, "attack_id": spec.id, "goal": spec.goal}
