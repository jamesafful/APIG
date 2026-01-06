from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .types import ToolCall, ToolResult
import json

@dataclass
class SandboxState:
    """Holds deterministic environment state."""
    files: Dict[str, str]
    inbox: List[Dict[str, Any]]
    web: Dict[str, str]
    retrieved_docs: Dict[str, List[Dict[str, str]]]
    forms: Dict[str, Dict[str, Any]]
    outbox: List[Dict[str, Any]]
    http_posts: List[Dict[str, Any]]
    # Optional adaptive content sources (Tier C). Each tool call may reveal a
    # different stage (e.g., repeated web_fetch returns progressively more
    # persuasive injections).
    adaptive_web: Dict[str, List[str]] = field(default_factory=dict)
    adaptive_docs: Dict[str, List[List[Dict[str, str]]]] = field(default_factory=dict)
    adaptive_counters: Dict[str, int] = field(default_factory=dict)

class ToolRouter:
    def __init__(self, state: SandboxState):
        self.state = state

    def run(self, call: ToolCall) -> ToolResult:
        name = call.name
        a = call.args or {}
        try:
            if name == "read_file":
                path = str(a["path"])
                return ToolResult(True, self.state.files.get(path, ""))
            if name == "write_file":
                path = str(a["path"]); content = str(a.get("content",""))
                self.state.files[path] = content
                return ToolResult(True, {"written": path, "bytes": len(content)})
            if name == "send_email":
                msg = {"to": a.get("to"), "subject": a.get("subject",""), "body": a.get("body","")}
                self.state.outbox.append(msg)
                return ToolResult(True, {"sent": True})
            if name == "http_post":
                rec = {"url": a.get("url"), "body": a.get("body","")}
                self.state.http_posts.append(rec)
                return ToolResult(True, {"status": 200})
            if name == "web_fetch":
                url = str(a["url"])
                # Adaptive stage selection
                if url in self.state.adaptive_web:
                    k = f"web:{url}"
                    idx = self.state.adaptive_counters.get(k, 0)
                    stages = self.state.adaptive_web[url]
                    html = stages[min(idx, len(stages) - 1)] if stages else ""
                    self.state.adaptive_counters[k] = idx + 1
                    return ToolResult(True, {"url": url, "html": html, "stage": min(idx, len(stages) - 1)})
                return ToolResult(True, {"url": url, "html": self.state.web.get(url, "")})
            if name == "retrieve_docs":
                query = str(a.get("query",""))
                if query in self.state.adaptive_docs:
                    k = f"docs:{query}"
                    idx = self.state.adaptive_counters.get(k, 0)
                    stages = self.state.adaptive_docs[query]
                    docs = stages[min(idx, len(stages) - 1)] if stages else []
                    self.state.adaptive_counters[k] = idx + 1
                    return ToolResult(True, docs)
                return ToolResult(True, self.state.retrieved_docs.get(query, []))
            if name == "fill_form":
                form_id = str(a["form_id"])
                fields = dict(a.get("fields", {}))
                self.state.forms.setdefault(form_id, {"fields": {}, "submitted": False})
                self.state.forms[form_id]["fields"].update(fields)
                return ToolResult(True, {"filled": True, "form_id": form_id})
            if name == "submit_form":
                form_id = str(a["form_id"])
                self.state.forms.setdefault(form_id, {"fields": {}, "submitted": False})
                self.state.forms[form_id]["submitted"] = True
                return ToolResult(True, {"submitted": True, "form_id": form_id, "fields": self.state.forms[form_id]["fields"]})
            return ToolResult(False, None, f"Unknown tool: {name}")
        except Exception as e:
            return ToolResult(False, None, f"Tool error: {e}")
