# APIG v0.1 (Agentic Prompt Injection Gauntlet)

This repository is a **deterministic** benchmark harness for evaluating tool-using agents under
**indirect prompt injection** and **tool-output injection**.

It ships with:
- A sandbox environment with mocked tools (web, email, file system, retrieval)
- 3 suites (Inbox, RAG Policy/Compliance, Web Form) with clean tasks + injected variants
- AttackSpec YAML format + an "attack compiler" that renders injected payloads into content channels
- Mechanical checkers:
  - **UAR** (Unauthorized Action Rate): forbidden tool calls attempted
  - **SER** (Sensitive Egress Rate): canary/PII values leaving via outbound channels
  - **CTS** (Clean Task Success): success on clean tasks
- A baseline **RuleBasedAgent** and a **NaiveLLMAgent** stub to plug in real models later.

> Notes:
> - This is v0.1: it focuses on Tier A/B (indirect injection + tool-output injection).
> - No network calls are performed; everything is sandboxed and reproducible.

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
