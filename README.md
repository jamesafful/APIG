# APIG v0.1 (Agentic Prompt Injection Gauntlet)

This repository is a **deterministic** benchmark harness for evaluating tool-using agents under
**indirect prompt injection** and **tool-output injection**.

It ships with:
- A sandbox environment with mocked tools (web, email, file system, retrieval)
- 3 suites (Inbox, RAG Policy/Compliance, Web Form) with clean tasks + injected variants
- AttackSpec YAML format + an "attack compiler" that renders injected payloads into content channels
- Mechanical checkers:
  - **UAR_attempted / UAR_executed**: unauthorized tool use attempted vs executed
  - **SER_attempted / SER_executed**: sensitive egress attempted vs executed
  - **CTS** (Clean Task Success): success on clean tasks
- Agents:
  - **RuleBasedAgent** (safe baseline)
  - **NaiveLLMAgent** (intentionally vulnerable stub)
  - **LLM-backed agents**: `llm_naive` / `llm_defended` (OpenAI or Gemini) with JSON-only tool calling and optional SQLite caching

> Notes:
> - This is still "v0.1" in spirit, but includes an initial Tier C mechanism: **adaptive staged injections** for repeated `web_fetch` / `retrieve_docs` calls.
> - LLM-backed agents require outbound network access and API keys; the sandbox tools remain deterministic.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run one suite with the baseline agent
apig run --suite inbox --agent rule --episodes 10 --seed 42

# Run all suites and write a JSON report
apig run --suite all --agent rule --episodes 50 --seed 42 --out report.json

# Validate AttackSpec files
apig validate attacks/
```


```bash
export OPENAI_API_KEY="YOUR_KEY"
python -m apig.cli run \
  --suite all \
  --agent llm_naive \
  --episodes 5 \
  --seed 42 \
  --llm-provider openai \
  --llm-model gpt-4.1-mini \
  --llm-cache-path .apig_cache.sqlite \
  --out report_openai_llm.json


export GEMINI_API_KEY="YOUR_KEY"
python -m apig.cli run \
  --suite all \
  --agent llm_defended \
  --episodes 5 \
  --seed 42 \
  --llm-provider gemini \
  --llm-model gemini-1.5-pro \
  --llm-cache-path .apig_cache.sqlite \
  --out report_gemini_llm.json
```

## Project layout

- `apig/` core library
  - `env/` sandbox and tools
  - `suites/` task definitions
  - `attacks/` AttackSpec parsing/compilation helpers
  - `agents/` baseline agents
  - `scoring/` metrics and aggregation
- `attacks/` example AttackSpec YAMLs
- `configs/` runner configs
- `tests/` unit tests

## Extending
To add a new suite:
1. Create `apig/suites/<name>.py` with tasks
2. Register it in `apig/suites/registry.py`

To plug in a real model:
- Implement `apig/agents/base.py::Agent` interface.
- Use the tool request/response types in `apig/env/types.py`.

## License
MIT
