from __future__ import annotations
import json
import typer
from rich.console import Console
from rich.table import Table
from pathlib import Path
from typing import Optional, List

from apig.suites.registry import get_suite, SUITES
from apig.agents.registry import get_agent, AGENTS
from apig.env.tools import SandboxState
from apig.attacks.io import load_attack_file
from apig.harness import run_task
from apig.scoring import summarize, to_dict

app = typer.Typer(add_completion=False)
console = Console()

def _load_attacks(paths: List[str]) -> List:
    attacks = []
    for p in paths:
        attacks.extend(load_attack_file(p))
    return attacks

@app.command()
def validate(path: str = typer.Argument(..., help="Path to attacks folder or YAML file")):
    p = Path(path)
    files = []
    if p.is_dir():
        files = list(p.glob("*.yml")) + list(p.glob("*.yaml"))
    else:
        files = [p]
    ok = True
    for f in files:
        try:
            _ = load_attack_file(str(f))
            console.print(f"[green]OK[/green] {f}")
        except Exception as e:
            ok = False
            console.print(f"[red]FAIL[/red] {f}: {e}")
    raise typer.Exit(code=0 if ok else 1)

@app.command()
def run(
    suite: str = typer.Option("all", help=f"Suite name: one of {list(SUITES)} or 'all'"),
    agent: str = typer.Option("rule", help=f"Agent: one of {list(AGENTS)}"),
    episodes: int = typer.Option(10, help="Episodes per task variant (clean + attacked variants)."),
    seed: int = typer.Option(0, help="Deterministic seed (currently used only for episode id)."),
    attacks: List[str] = typer.Option([], help="Attack YAML files/folders. If omitted, uses built-in examples in ./attacks"),
    out: Optional[str] = typer.Option(None, help="Write full JSON results to this path."),
):
    agent_obj = get_agent(agent)

    # attacks
    attack_specs = []
    if attacks:
        # expand folders
        paths = []
        for a in attacks:
            ap = Path(a)
            if ap.is_dir():
                paths.extend([str(x) for x in list(ap.glob("*.yml")) + list(ap.glob("*.yaml"))])
            else:
                paths.append(str(ap))
        attack_specs = _load_attacks(paths)
    else:
        # default example attacks
        default_dir = Path(__file__).resolve().parent.parent / "attacks"
        paths = [str(x) for x in list(default_dir.glob("*.yml")) + list(default_dir.glob("*.yaml"))]
        attack_specs = _load_attacks(paths)

    suite_names = list(SUITES) if suite == "all" else [suite]
    all_results = []

    for sn in suite_names:
        s = get_suite(sn)
        # For v0.1, we run: clean task + a small sample of attacks (first 3 attacks)
        atk_sample = attack_specs[:3] if attack_specs else []
        variants = [None] + atk_sample

        for atk in variants:
            tasks = s.tasks(atk)
            for task in tasks:
                for i in range(episodes):
                    # fresh state for determinism
                    st = SandboxState(files={}, inbox=[], web={}, retrieved_docs={}, forms={}, outbox=[], http_posts=[])
                    task.setup(st, atk)
                    # canaries: pull from state by regex convention
                    canaries = []
                    # harvest canaries from any state strings
                    for v in list(st.files.values()) + [m.get("body","") for m in st.inbox] + list(st.web.values()):
                        for m in __import__("re").findall(r"CANARY-[A-Z0-9\-]+", str(v)):
                            canaries.append(m)
                    # run
                    res = run_task(agent_obj, task, st, sorted(set(canaries)), sn, seed, i)
                    all_results.append(res)

    summary = summarize(all_results)

    table = Table(title=f"APIG v0.1 results (agent={agent}, suite={suite})")
    table.add_column("Metric")
    table.add_column("Value")
    for k, v in to_dict(summary).items():
        table.add_row(k, f"{v:.3f}" if isinstance(v, float) else str(v))
    console.print(table)

    if out:
        data = {
            "summary": to_dict(summary),
            "episodes": [
                {
                    "episode_id": r.episode_id,
                    "suite": r.suite,
                    "task_id": r.task_id,
                    "attacked": r.attacked,
                    "success": r.success,
                    "uar": r.uar,
                    "ser": r.ser,
                    "forbidden_calls": [{"name": c.name, "args": c.args} for c in r.forbidden_calls],
                    "egress_hits": r.egress_hits,
                    "trace": [{"t": e.t, "kind": e.kind, "data": e.data} for e in r.trace],
                }
                for r in all_results
            ]
        }
        Path(out).write_text(json.dumps(data, indent=2), encoding="utf-8")
        console.print(f"Wrote report to {out}")

if __name__ == "__main__":
    app()
