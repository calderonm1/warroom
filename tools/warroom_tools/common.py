from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

SKIP_DIRS = {".git", ".venv", "node_modules", "Library", "Temp", "obj", "bin", ".terraform", "__pycache__"}

# Requirement and decision IDs that docs define and stories cite.
REF_PATTERN = re.compile(
    r"\b(ADR-\d{4}|GDD-[A-Z]+-\d{3}|SIM-\d{3}|NFR-[A-Z]+-\d{3}[a-z]?|BR-\d{3}|PR-\d{3}|SCR-\d{3}"
    r"|GLB-\d{3}|KPI-\d{2}|CONV-[A-Z]+-\d{3}|RISK-\d{3}|OQ-\d{3})\b"
)
BACKLOG_ID_PATTERN = re.compile(r"\b(EP-\d{2}|FE-\d{2}\.\d+|ST-\d{2}\.\d+\.\d+)\b")


def repo_root(start: Path | None = None) -> Path:
    env = os.environ.get("WR_REPO_ROOT")
    if env:
        return Path(env).resolve()
    here = (start or Path.cwd()).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / "AGENTS.md").exists() and (candidate / "backlog").is_dir():
            return candidate
    raise RuntimeError("Could not find the War Room repo root (AGENTS.md and backlog/). Set WR_REPO_ROOT.")


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def iter_files(root: Path, suffixes: tuple[str, ...]) -> list[Path]:
    out: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if name.endswith(suffixes):
                out.append(Path(dirpath) / name)
    return out


def rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


@dataclass
class Report:
    """Collects findings so every checker prints the same machine-parsable format."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, where: str, message: str) -> None:
        self.errors.append(f"ERROR {where}: {message}")

    def warn(self, where: str, message: str) -> None:
        self.warnings.append(f"WARN  {where}: {message}")

    @property
    def ok(self) -> bool:
        return not self.errors

    def print(self, label: str) -> None:
        for line in [*self.errors, *self.warnings]:
            print(line)
        status = "ok" if self.ok else "failed"
        print(f"{label}: {status} ({len(self.errors)} errors, {len(self.warnings)} warnings)")


def defined_refs(root: Path) -> set[str]:
    """All requirement IDs mentioned anywhere under docs/, plus ADR IDs that have a file."""
    found: set[str] = set()
    for path in iter_files(root / "docs", (".md",)):
        found.update(REF_PATTERN.findall(path.read_text(encoding="utf-8")))
    found = {r for r in found if not r.startswith("ADR-")}
    for adr in (root / "docs" / "adr").glob("[0-9][0-9][0-9][0-9]-*.md"):
        number = adr.name[:4]
        if number != "0000":
            found.add(f"ADR-{number}")
    return found
