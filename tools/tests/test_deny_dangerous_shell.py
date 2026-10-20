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


def test_denies_push_forms_the_literal_regex_missed():
    assert run_hook("git -C /workspace push origin main")["permission"] == "deny"
    assert run_hook("git -C /workspace push --force origin master")["permission"] == "deny"
    assert run_hook("git push origin +main")["permission"] == "deny"
    assert run_hook("git push --force origin +refs/heads/main")["permission"] == "deny"
    assert run_hook("git push origin 'main'")["permission"] == "deny"
    assert run_hook('git push origin "HEAD:main"')["permission"] == "deny"
    assert run_hook("git push origin :main")["permission"] == "deny"
    assert run_hook("git push --all origin")["permission"] == "deny"
    assert run_hook("git push --mirror origin")["permission"] == "deny"
    assert run_hook('bash -lc "git push origin main"')["permission"] == "deny"


def test_denies_terraform_chdir_and_gh_repo_flag():
    assert run_hook("terraform -chdir=infra apply -auto-approve")["permission"] == "deny"
    assert run_hook("terraform -chdir=infra/envs/dev/core destroy -auto-approve")["permission"] == "deny"
    assert run_hook("gh -R acme/warroom pr merge 7 --squash")["permission"] == "deny"
    assert run_hook("gh --repo acme/warroom pr merge 7")["permission"] == "deny"


def test_allows_nearby_commands_that_are_not_the_protected_action():
    assert run_hook("git -C /tmp/main push -u origin feature/ST-01.3.6")["permission"] == "allow"
    assert run_hook("git push origin main:feature")["permission"] == "allow"
    assert run_hook("git push origin feature/main-fix")["permission"] == "allow"
    assert run_hook('git commit -m "update main" && git push -u origin feature/ST-01.3.6')["permission"] == "allow"
    assert run_hook("git add --all && git push -u origin HEAD")["permission"] == "allow"
    assert run_hook("terraform -chdir=infra plan")["permission"] == "allow"
    assert run_hook("gh pr view 7")["permission"] == "allow"
    assert run_hook("gh pr comment 1 --body merge")["permission"] == "allow"
