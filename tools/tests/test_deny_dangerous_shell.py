from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parents[2] / ".cursor" / "hooks" / "deny-dangerous-shell.py"


def run_hook(command: str) -> dict:
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps({"command": command}),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def test_denies_gh_pr_merge():
    out = run_hook("gh pr merge 7 --squash")
    assert out["permission"] == "deny"


def test_denies_terraform_apply_and_destroy():
    assert run_hook("terraform apply -auto-approve")["permission"] == "deny"
    assert run_hook("terraform destroy")["permission"] == "deny"


def test_denies_push_and_force_push_to_main():
    assert run_hook("git push origin main")["permission"] == "deny"
    assert run_hook("git push --force origin main")["permission"] == "deny"
    assert run_hook("git push -f origin HEAD:main")["permission"] == "deny"


def test_allows_feature_push_plan_and_make():
    assert run_hook("git push -u origin HEAD")["permission"] == "allow"
    assert run_hook("git push --force-with-lease origin feat/ST-01.3.5-agent-skills-hooks")["permission"] == "allow"
    assert run_hook("terraform plan -out=tfplan")["permission"] == "allow"
    assert run_hook("make check")["permission"] == "allow"
