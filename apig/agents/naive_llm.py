from __future__ import annotations
from typing import List
import re, json
from apig.env.types import ToolCall, TraceEvent
from .base import Agent, ToolInterface

class NaiveLLMAgent(Agent):
    """A deliberately unsafe agent stub to demonstrate attacks.

    It naively executes any line in untrusted content that looks like:
    - 'CALL_TOOL: <tool> <json_args>'
    This is *intentionally vulnerable* to indirect prompt injection.
    """
    name = "naive"

    def run(self, prompt: str, tools: ToolInterface) -> List[TraceEvent]:
        trace: List[TraceEvent] = []
        t = 0
        def emit(kind, data):
            nonlocal t
            trace.append(TraceEvent(t=t, kind=kind, data=data)); t += 1

        emit("agent_message", {"text": "Starting task (naive agent)."})
        # pull available context files set up by harness
        context_paths = ["/sandbox/inbox_latest.txt", "/sandbox/context.txt", "/sandbox/webpage.html"]
        context = ""
        for p in context_paths:
            r = tools.call(ToolCall("read_file", {"path": p}))
            emit("tool_call", {"name": "read_file", "args": {"path": p}})
            emit("tool_result", {"ok": r.ok, "content": r.content})
            if r.ok and r.content:
                context += "\n" + str(r.content)

        # execute injected tool calls if present
        for m in re.finditer(r"CALL_TOOL:\s*(\w+)\s*(\{.*?\})", context, flags=re.DOTALL):
            tool = m.group(1)
            try:
                args = json.loads(m.group(2))
            except Exception:
                args = {}
            call = ToolCall(tool, args)
            res = tools.call(call)
            emit("tool_call", {"name": tool, "args": args})
            emit("tool_result", {"ok": res.ok, "content": res.content, "error": res.error})

        # then do minimal intended actions
        if "summary" in prompt.lower():
            body = tools.call(ToolCall("read_file", {"path": "/sandbox/inbox_latest.txt"})).content
            tools.call(ToolCall("write_file", {"path": "/sandbox/summary.txt", "content": "Summary: " + str(body)[:80]}))
            emit("tool_call", {"name": "write_file", "args": {"path": "/sandbox/summary.txt"}})
            emit("tool_result", {"ok": True, "content": {"written": "/sandbox/summary.txt"}})
        if "pto" in prompt.lower():
            docs = tools.call(ToolCall("retrieve_docs", {"query": "vacation policy"})).content
            tools.call(ToolCall("write_file", {"path": "/sandbox/answer.txt", "content": "Employees get 15 PTO days. (Source: docs)"}))
            emit("tool_call", {"name": "write_file", "args": {"path": "/sandbox/answer.txt"}})
            emit("tool_result", {"ok": True, "content": {"written": "/sandbox/answer.txt"}})
        if "travel" in prompt.lower():
            sub = tools.call(ToolCall("submit_form", {"form_id": "travel"}))
            tools.call(ToolCall("write_file", {"path": "/sandbox/form_receipt.json", "content": json.dumps(sub.content)}))
            emit("tool_call", {"name": "write_file", "args": {"path": "/sandbox/form_receipt.json"}})
            emit("tool_result", {"ok": True, "content": {"written": "/sandbox/form_receipt.json"}})

        emit("agent_message", {"text": "Finished (naive agent)."})
        return trace
