from __future__ import annotations
from typing import List
import yaml
from .schema import AttackSpec

def load_attack_file(path: str) -> List[AttackSpec]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if isinstance(data, dict) and "attacks" in data:
        data = data["attacks"]
    if not isinstance(data, list):
        raise ValueError("Attack YAML must be a list or contain 'attacks:' list")
    return [AttackSpec.model_validate(x) for x in data]
