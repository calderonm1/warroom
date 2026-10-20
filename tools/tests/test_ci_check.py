"""Workflow convention checks (ST-04.1.1)."""

from __future__ import annotations

from pathlib import Path

import pytest
from conftest import REAL_ROOT

from warroom_tools import ci_check
from warroom_tools.cli import main

CHECKOUT = "actions/checkout@11d5960a326750d5838078e36cf38b85af677262"
UPSTREAM = "astral-sh/setup-uv@d0cc045d04ccac9d8b7881df0226f9e82c39688e"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _setup_actions(root: Path, uses: str = UPSTREAM) -> None:
    for name in ci_check.SETUP_ACTIONS:
        _write(
            root / ".github" / "actions" / name / "action.yml",
            f"name: {name}\ndescription: setup\nruns:\n  using: composite\n  steps:\n    - uses: {uses}\n",
        )


def _workflow(body: str) -> str:
    return f"name: demo\n{body}\njobs:\n  demo:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: {CHECKOUT}\n"


def _repo(tmp_path: Path, workflow: str) -> Path:
    root = tmp_path / "repo"
    _setup_actions(root)
    _write(root / ".github" / "workflows" / "demo.yml", workflow)
    return root


FILTERED_PUSH = """\
on:
  push:
    paths: ["**"]
concurrency:
  group: demo
  cancel-in-progress: true
"""


def test_real_workflows_follow_conventions():
    report = ci_check.validate(REAL_ROOT)
    assert report.ok, "\n".join(report.errors)


def test_rejects_floating_action_tag(tmp_path: Path):
    workflow = _workflow(FILTERED_PUSH).replace(CHECKOUT, "actions/checkout@v4")
    root = _repo(tmp_path, workflow)
    errors = ci_check.validate(root).errors
    assert any("commit SHA" in error for error in errors)


def test_rejects_missing_path_filter(tmp_path: Path):
    body = """\
on:
  pull_request:
  push:
    branches: [main]
concurrency:
  group: demo
  cancel-in-progress: true
"""
    root = _repo(tmp_path, _workflow(body))
    errors = ci_check.validate(root).errors
    assert any("paths or paths-ignore" in error for error in errors)


def test_rejects_missing_concurrency(tmp_path: Path):
    body = """\
on:
  push:
    paths: ["**"]
"""
    root = _repo(tmp_path, _workflow(body))
    errors = ci_check.validate(root).errors
    assert any("concurrency group" in error for error in errors)


def test_accepts_paths_ignore_and_local_action(tmp_path: Path):
    body = """\
on:
  pull_request:
    paths-ignore: ["docs/**"]
concurrency:
  group: demo-${{ github.ref }}
  cancel-in-progress: true
"""
    workflow = _workflow(body) + "      - uses: ./.github/actions/setup-uv\n"
    root = _repo(tmp_path, workflow)
    assert ci_check.validate(root).errors == []


def test_schedule_only_workflow_needs_no_path_filter(tmp_path: Path):
    body = """\
on:
  schedule:
    - cron: "0 0 * * *"
concurrency:
  group: nightly
  cancel-in-progress: false
"""
    root = _repo(tmp_path, _workflow(body))
    assert ci_check.validate(root).errors == []


def test_rejects_missing_setup_action(tmp_path: Path):
    root = _repo(tmp_path, _workflow(FILTERED_PUSH))
    (root / ".github" / "actions" / "setup-buf" / "action.yml").unlink()
    errors = ci_check.validate(root).errors
    assert any("setup-buf" in error and "missing" in error for error in errors)


def test_cli_real_repo_exits_zero(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    monkeypatch.setenv("WR_REPO_ROOT", str(REAL_ROOT))
    assert main(["ci", "check"]) == 0
    captured = capsys.readouterr()
    assert "ci-check: ok" in captured.out
