from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Any
from apig.env.tools import SandboxState
from apig.env.policy import Policy
from apig.attacks.schema import AttackSpec

@dataclass
class Task:
    task_id: str
    prompt: str
    setup: Callable[[SandboxState, Optional[AttackSpec]], None]
    success_check: Callable[[SandboxState], bool]
    policy: Policy
    attacked: bool = False
    attack: Optional[AttackSpec] = None

class Suite:
    name: str
    def tasks(self, attack: Optional[AttackSpec] = None) -> List[Task]:
        raise NotImplementedError
