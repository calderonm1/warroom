from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from .common import Report, load_yaml, rel

EXPECTED_ENVIRONMENTS = ("local", "dev", "staging", "prod")
PROD_FORBIDDEN = ("can_deploy", "can_apply_infra", "can_run_admin_writes")


def validate(root: Path) -> Report:
    report = Report()
    env_dir = root / "ops" / "environments"
    schema = json.loads((env_dir / "schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    found = set()
    for path in sorted(env_dir.glob("*.yaml")):
        where = rel(path, root)
        data = load_yaml(path)
        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
        for err in errors:
            location = "/".join(str(p) for p in err.absolute_path) or "<root>"
            report.error(where, f"schema: {location}: {err.message}")
        if errors:
            continue
        found.add(data["name"])
        if data["name"] != path.stem:
            report.error(where, f"name '{data['name']}' must match file name '{path.stem}'")
        policy = data["agent_policy"]
        if data["name"] == "prod":
            for key in PROD_FORBIDDEN:
                if policy.get(key):
                    report.error(where, f"agent_policy.{key} must be false in prod (ADR-0018)")
        if data["name"] == "staging" and policy.get("can_apply_infra"):
            report.error(where, "agent_policy.can_apply_infra must be false in staging (ADR-0018)")
        if data["status"] == "active":
            for key, value in data["endpoints"].items():
                if "TBD" in value:
                    report.error(where, f"active environment has TBD endpoint '{key}'")
            if data["name"] != "local" and data["aws"].get("account_id") in (None, "TBD"):
                report.error(where, "active environment needs a real aws.account_id")
        for runbook in data.get("runbooks", []):
            if not (root / runbook.split("#", 1)[0]).exists():
                report.error(where, f"runbook path does not exist: {runbook}")

    for name in EXPECTED_ENVIRONMENTS:
        if name not in found:
            report.error("ops/environments", f"missing or invalid manifest for '{name}'")
    return report
