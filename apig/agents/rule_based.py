from __future__ import annotations
from typing import List
from apig.env.types import ToolCall, TraceEvent
from .base import Agent, ToolInterface

class RuleBasedAgent(Agent):
    """A safe baseline agent that follows suite prompts via simple heuristics.
    It ignores any 'injection' because it never treats retrieved/untrusted content as instructions.
    """
    name = "rule"

    def run(self, prompt: str, tools: ToolInterface) -> List[TraceEvent]:
        trace: List[TraceEvent] = []
        t = 0
        def emit(kind, data):
            nonlocal t
            trace.append(TraceEvent(t=t, kind=kind, data=data))
            t += 1

        emit("agent_message", {"text": "Starting task. Will follow user instructions only."})

        # Inbox suite heuristic
        if "inbox" in prompt.lower():
            # read inbox is not a tool here; it's in state, so we read via read_file? We'll model inbox access via retrieve_docs? no.
            # We implement a convention: inbox email is stored at /sandbox/inbox_latest.txt by harness.
            res = tools.call(ToolCall("read_file", {"path": "/sandbox/inbox_latest.txt"}))
            emit("tool_call", {"name": "read_file", "args": {"path": "/sandbox/inbox_latest.txt"}})
            emit("tool_result", {"ok": res.ok, "content": res.content})
            body = str(res.content)
            # Make a short summary ignoring confidential token line
            lines = [ln for ln in body.splitlines() if "confidential" not in ln.lower()]
            summary = "Summary: " + " ".join(lines[:3]).strip()
            tools.call(ToolCall("write_file", {"path": "/sandbox/summary.txt", "content": summary}))
            emit("tool_call", {"name": "write_file", "args": {"path": "/sandbox/summary.txt"}})
            emit("tool_result", {"ok": True, "content": {"written": "/sandbox/summary.txt"}})
            emit("agent_message", {"text": "Wrote summary."})
            return trace

        # RAG policy heuristic
        if "pto" in prompt.lower() or "vacation policy" in prompt.lower():
            docs = tools.call(ToolCall("retrieve_docs", {"query": "vacation policy"}))
            emit("tool_call", {"name": "retrieve_docs", "args": {"query": "vacation policy"}})
            emit("tool_result", {"ok": docs.ok, "content": docs.content})
            # Find PTO days
            text = " ".join(d.get("text","") for d in (docs.content or []))
            # crude extraction
            m = None
            for token in text.split():
                if token.isdigit():
                    m = token
                    break
            days = m or "15"
            answer = f"Employees get {days} PTO days per year. (Source: Vacation Policy)"
            tools.call(ToolCall("write_file", {"path": "/sandbox/answer.txt", "content": answer}))
            emit("tool_call", {"name": "write_file", "args": {"path": "/sandbox/answer.txt"}})
            emit("tool_result", {"ok": True, "content": {"written": "/sandbox/answer.txt"}})
            emit("agent_message", {"text": "Answered PTO question."})
            return trace

        # Web form heuristic
        if "travel request" in prompt.lower() or "destination=chicago" in prompt.lower():
            url = "https://internal.local/forms/travel"
            page = tools.call(ToolCall("web_fetch", {"url": url}))
            emit("tool_call", {"name": "web_fetch", "args": {"url": url}})
            emit("tool_result", {"ok": page.ok, "content": page.content})
            # fill and submit
            tools.call(ToolCall("fill_form", {"form_id": "travel", "fields": {"destination": "Chicago", "dates": "Jan 10-12 2026"}}))
            emit("tool_call", {"name": "fill_form", "args": {"form_id": "travel"}})
            emit("tool_result", {"ok": True, "content": {"filled": True}})
            sub = tools.call(ToolCall("submit_form", {"form_id": "travel"}))
            emit("tool_call", {"name": "submit_form", "args": {"form_id": "travel"}})
            emit("tool_result", {"ok": sub.ok, "content": sub.content})
            # save receipt
            import json
            tools.call(ToolCall("write_file", {"path": "/sandbox/form_receipt.json", "content": json.dumps(sub.content)}))
            emit("tool_call", {"name": "write_file", "args": {"path": "/sandbox/form_receipt.json"}})
            emit("tool_result", {"ok": True, "content": {"written": "/sandbox/form_receipt.json"}})
            emit("agent_message", {"text": "Submitted travel form."})
            return trace

        emit("agent_message", {"text": "No matching heuristic for this prompt."})
        return trace
