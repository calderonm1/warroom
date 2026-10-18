from __future__ import annotations

import datetime as dt
import re
from pathlib import Path
from typing import Any

import yaml

from .common import Report, iter_files, rel

REQUIRED_KEYS = ("title", "status", "owner", "last_reviewed", "related")
STATUSES = {"draft", "review", "accepted", "superseded", "deprecated"}
TEMPLATE_FILES = {"docs/adr/0000-template.md"}
FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
FENCE = re.compile(r"^(```|~~~).*?^\1", re.DOTALL | re.MULTILINE)
INLINE_CODE = re.compile(r"`[^`\n]*`")
LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
ADR_REF = re.compile(r"^ADR-(\d{4})$")
PATH_LIKE = re.compile(r"(/|\.(md|ya?ml|json|mdc|toml)$)")
EXTERNAL = ("http://", "https://", "mailto:", "tel:")
LINK_SCAN_ROOTS = [
    "docs",
    "backlog",
    "ops",
    "design",
    "client",
    "server",
    "shared",
    "content",
    "infra",
    "tools",
]


def parse_front_matter(text: str) -> dict[str, Any] | None:
    match = FRONT_MATTER.match(text)
    if not match:
        return None
    data = yaml.safe_load(match.group(1))
    return data if isinstance(data, dict) else None


def strip_code(text: str) -> str:
    return INLINE_CODE.sub("", FENCE.sub("", text))


def links_in(text: str) -> list[str]:
    return LINK.findall(strip_code(text))


def _as_date(value: Any) -> dt.date | None:
    if isinstance(value, dt.date):
        return value
    try:
        return dt.date.fromisoformat(str(value))
    except ValueError:
        return None


def _check_front_matter(root: Path, path: Path, text: str, report: Report) -> None:
    where = rel(path, root)
    try:
        fm = parse_front_matter(text)
    except yaml.YAMLError as exc:
        report.error(where, f"front matter is not valid YAML: {' '.join(str(exc).split())} (CONV-DOC-001)")
        return
    if fm is None:
        report.error(where, "missing YAML front matter (CONV-DOC-001)")
        return
    for key in REQUIRED_KEYS:
        if key not in fm:
            report.error(where, f"front matter missing '{key}' (CONV-DOC-001)")
    status = fm.get("status")
    if status is not None and status not in STATUSES:
        report.error(where, f"front matter status '{status}' not in {sorted(STATUSES)}")
    if where not in TEMPLATE_FILES and "last_reviewed" in fm and _as_date(fm["last_reviewed"]) is None:
        report.error(where, f"last_reviewed '{fm['last_reviewed']}' is not an ISO date")
    related = fm.get("related", [])
    if not isinstance(related, list):
        report.error(where, "related must be a list")
        return
    if where in TEMPLATE_FILES:
        return
    for entry in related:
        entry = str(entry)
        adr = ADR_REF.match(entry)
        if adr:
            if not list((root / "docs" / "adr").glob(f"{adr.group(1)}-*.md")):
                report.error(where, f"related {entry} has no ADR file (CONV-DOC-003)")
        elif PATH_LIKE.search(entry) and not (root / entry.split("#", 1)[0]).exists():
            report.error(where, f"related path does not exist: {entry} (CONV-DOC-003)")


def _check_links(root: Path, path: Path, text: str, report: Report) -> None:
    where = rel(path, root)
    for target in links_in(text):
        if target.startswith(EXTERNAL) or target.startswith("#"):
            continue
        target_path = target.split("#", 1)[0]
        resolved = (path.parent / target_path).resolve()
        if not resolved.exists():
            report.error(where, f"broken link: {target} (CONV-DOC-003)")


def _markdown_files(root: Path) -> list[Path]:
    files = [p for p in root.glob("*.md")]
    for d in LINK_SCAN_ROOTS:
        if (root / d).is_dir():
            files.extend(iter_files(root / d, (".md",)))
    return sorted(set(files))


def check(root: Path) -> Report:
    report = Report()
    docs_dir = root / "docs"
    index = docs_dir / "README.md"
    docs = iter_files(docs_dir, (".md",))

    for path in docs:
        _check_front_matter(root, path, path.read_text(encoding="utf-8"), report)

    for path in _markdown_files(root):
        _check_links(root, path, path.read_text(encoding="utf-8"), report)

    if not index.exists():
        report.error("docs/README.md", "missing documentation index (CONV-DOC-002)")
    else:
        linked = {
            (index.parent / t.split("#", 1)[0]).resolve()
            for t in links_in(index.read_text(encoding="utf-8"))
            if not t.startswith(EXTERNAL)
        }
        for path in docs:
            if path.resolve() != index.resolve() and path.resolve() not in linked:
                report.error(rel(path, root), "not linked from docs/README.md (CONV-DOC-002)")
    return report


def stale(root: Path, days: int = 180, today: dt.date | None = None) -> list[tuple[str, dt.date, int]]:
    today = today or dt.date.today()
    out = []
    for path in iter_files(root / "docs", (".md",)):
        where = rel(path, root)
        if where in TEMPLATE_FILES:
            continue
        try:
            fm = parse_front_matter(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            continue
        reviewed = _as_date(fm.get("last_reviewed"))
        if reviewed is None:
            continue
        age = (today - reviewed).days
        if age > days:
            out.append((where, reviewed, age))
    return sorted(out, key=lambda r: -r[2])
