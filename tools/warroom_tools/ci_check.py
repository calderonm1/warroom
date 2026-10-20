"""Checks GitHub Actions workflows follow the conventions in docs/06-environments/ci-cd.md."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from .common import Report, load_yaml, rel

SETUP_ACTIONS = ("setup-dotnet", "setup-uv", "setup-buf")
FILTERED_EVENTS = ("pull_request", "pull_request_target", "push")
PATH_KEYS = ("paths", "paths-ignore")
REMOTE_PIN = re.compile(r"^[^.\s][^@\s]*@[0-9a-f]{40}$")


def validate(root: Path) -> Report:
    report = Report()
    for name in SETUP_ACTIONS:
        _check_setup_action(root, name, report)
    for path in _action_files(root):
        data = _load(path, root, report)
        if isinstance(data, dict):
            _check_uses(data, rel(path, root), report)
    workflows = _workflow_files(root)
    if not workflows:
        report.error(".github/workflows", "no workflow files found")
        return report
    for path in workflows:
        where = rel(path, root)
        data = _load(path, root, report)
        if not isinstance(data, dict):
            continue
        _check_workflow(data, where, report)
        _check_uses(data, where, report)
    return report


def _check_setup_action(root: Path, name: str, report: Report) -> None:
    path = root / ".github" / "actions" / name / "action.yml"
    where = f".github/actions/{name}/action.yml"
    if not path.is_file():
        report.error(where, "missing composite setup action")
        return
    data = _load(path, root, report)
    if not isinstance(data, dict):
        return
    using = (data.get("runs") or {}).get("using") if isinstance(data.get("runs"), dict) else None
    if using != "composite":
        report.error(where, "setup action must be a composite action")
        return
    pinned = [value for _, value in _iter_uses(data) if isinstance(value, str) and REMOTE_PIN.match(value)]
    if not pinned:
        report.error(where, "setup action must call a third-party action pinned to a commit SHA")


def _check_workflow(data: dict, where: str, report: Report) -> None:
    triggers = _triggers(data)
    if not isinstance(triggers, dict):
        report.error(where, "workflow needs an 'on' mapping with path filters")
    else:
        saw_filtered_event = False
        for event in FILTERED_EVENTS:
            if event not in triggers:
                continue
            saw_filtered_event = True
            spec = triggers[event]
            if not _has_path_filter(spec):
                report.error(where, f"{event} trigger needs paths or paths-ignore")
        if not saw_filtered_event and not any(key not in FILTERED_EVENTS for key in triggers):
            report.error(where, "workflow needs a pull_request or push trigger with paths or paths-ignore")

    concurrency = data.get("concurrency")
    if not isinstance(concurrency, dict):
        report.error(where, "workflow needs a concurrency group")
        return
    group = concurrency.get("group")
    if not isinstance(group, str) or not group.strip():
        report.error(where, "concurrency.group must be a non-empty string")
    cancel = concurrency.get("cancel-in-progress")
    if not isinstance(cancel, bool | str) or (isinstance(cancel, str) and not cancel.strip()):
        report.error(where, "concurrency.cancel-in-progress must be set")


def _check_uses(data: dict, where: str, report: Report) -> None:
    for location, value in _iter_uses(data):
        if not isinstance(value, str):
            report.error(where, f"{location} uses must be a string")
            continue
        if value.startswith("./"):
            continue
        if REMOTE_PIN.match(value):
            continue
        report.error(
            where,
            f"{location} pins a third-party action to a tag or branch ({value}); use a 40-character commit SHA",
        )


def _triggers(data: dict):
    # PyYAML 1.1 parses the bare key `on` as boolean True.
    if "on" in data:
        return data["on"]
    if True in data:
        return data[True]
    return None


def _has_path_filter(spec: object) -> bool:
    if not isinstance(spec, dict):
        return False
    for key in PATH_KEYS:
        value = spec.get(key)
        if isinstance(value, list) and any(str(item).strip() for item in value):
            return True
    return False


def _iter_uses(node: object):
    if isinstance(node, dict):
        for key, value in node.items():
            if str(key) == "uses":
                yield "uses", value
            else:
                yield from _iter_uses(value)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_uses(item)


def _workflow_files(root: Path) -> list[Path]:
    workflow_dir = root / ".github" / "workflows"
    if not workflow_dir.is_dir():
        return []
    return sorted(path for path in workflow_dir.iterdir() if path.suffix in {".yml", ".yaml"} and path.is_file())


def _action_files(root: Path) -> list[Path]:
    action_dir = root / ".github" / "actions"
    if not action_dir.is_dir():
        return []
    return sorted(action_dir.glob("*/action.yml"))


def _load(path: Path, root: Path, report: Report):
    try:
        return load_yaml(path)
    except yaml.YAMLError as exc:
        report.error(rel(path, root), f"invalid YAML: {exc}")
        return None
