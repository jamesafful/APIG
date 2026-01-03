from apig.suites.registry import get_suite
from apig.agents.registry import get_agent
from apig.env.tools import SandboxState
from apig.harness import run_task

def test_rule_agent_inbox_clean():
    suite = get_suite("inbox")
    agent = get_agent("rule")
    task = suite.tasks(None)[0]
    st = SandboxState(files={}, inbox=[], web={}, retrieved_docs={}, forms={}, outbox=[], http_posts=[])
    task.setup(st, None)
    canaries = ["CANARY-API-KEY-12345"]
    res = run_task(agent, task, st, canaries, "inbox", 0, 0)
    assert res.success is True
    assert res.ser is False

def test_naive_agent_gets_blocked_on_external_email():
    suite = get_suite("inbox")
    agent = get_agent("naive")
    # build a direct attack spec inline by loading
    from apig.attacks.io import load_attack_file
    from pathlib import Path
    atk = load_attack_file(str(Path(__file__).resolve().parent.parent / "attacks" / "example.yml"))[0]
    task = suite.tasks(atk)[0]
    st = SandboxState(files={}, inbox=[], web={}, retrieved_docs={}, forms={}, outbox=[], http_posts=[])
    task.setup(st, atk)
    # canary present
    canaries = ["CANARY-API-KEY-12345"]
    res = run_task(agent, task, st, canaries, "inbox", 0, 0)
    assert res.uar is True  # attempted forbidden tool call
