from apig.attacks.io import load_attack_file
from pathlib import Path

def test_load_attack_file():
    p = Path(__file__).resolve().parent.parent / "attacks" / "example.yml"
    attacks = load_attack_file(str(p))
    assert len(attacks) >= 3
    assert attacks[0].id
