from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .common import BACKLOG_ID_PATTERN, Report, defined_refs, iter_files, load_yaml, rel

EPIC_FILE_PATTERN = re.compile(r"^(EP-\d{2})-[a-z0-9]+(?:-[a-z0-9]+)*\.yaml$")
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
FINISHED = {"done", "cancelled"}
READY_MAX_SIZES = {"XS", "S", "M"}

# Files outside backlog/ whose backlog ID mentions must resolve.
REFERENCE_SCAN_DIRS = ["docs", "ops", "design", "client", "server", "shared", "content", "infra", "tools"]
REFERENCE_SCAN_FILES = ["AGENTS.md", "README.md"]


@dataclass
class Story:
    data: dict[str, Any]
    feature_id: str
    epic_id: str
    milestone: str
    file: str

    @property
    def id(self) -> str:
        return self.data["id"]

    @property
    def status(self) -> str:
        return self.data["status"]

    @property
    def depends_on(self) -> list[str]:
        return list(self.data.get("depends_on", []))


@dataclass
class Backlog:
    epics: list[dict[str, Any]] = field(default_factory=list)
    epic_files: dict[str, str] = field(default_factory=dict)
    stories: dict[str, Story] = field(default_factory=dict)
    milestones: list[dict[str, Any]] = field(default_factory=list)

    def epic_stories(self, epic_id: str) -> list[Story]:
        return [s for s in self.stories.values() if s.epic_id == epic_id]

    def feature_stories(self, feature_id: str) -> list[Story]:
        return [s for s in self.stories.values() if s.feature_id == feature_id]


def derived_status(stories: list[Story]) -> str:
    statuses = {s.status for s in stories}
    active = [s for s in stories if s.status != "cancelled"]
    if active and all(s.status == "done" for s in active):
        return "done"
    if "in-progress" in statuses or any(s.status == "done" for s in active):
        return "in-progress"
    if "blocked" in statuses:
        return "blocked"
    if "ready" in statuses:
        return "ready"
    return "draft"


def load_schema(root: Path) -> dict[str, Any]:
    return json.loads((root / "backlog" / "schema" / "backlog.schema.json").read_text(encoding="utf-8"))


def load_backlog(root: Path, report: Report | None = None) -> Backlog:
    report = report or Report()
    validator = Draft202012Validator(load_schema(root))
    backlog = Backlog()

    milestones_path = root / "backlog" / "milestones.yaml"
    if milestones_path.exists():
        backlog.milestones = (load_yaml(milestones_path) or {}).get("milestones", [])
    else:
        report.error("backlog/milestones.yaml", "missing")

    for path in sorted((root / "backlog" / "epics").glob("*.yaml")):
        where = rel(path, root)
        match = EPIC_FILE_PATTERN.match(path.name)
        if not match:
            report.error(where, "file name must be EP-NN-<kebab-slug>.yaml")
        data = load_yaml(path)
        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
        for err in errors:
            location = "/".join(str(p) for p in err.absolute_path) or "<root>"
            report.error(where, f"schema: {location}: {err.message}")
        if errors:
            continue
        if match and match.group(1) != data["id"]:
            report.error(where, f"file name prefix {match.group(1)} does not match epic id {data['id']}")
        backlog.epics.append(data)
        backlog.epic_files[data["id"]] = where
        for feature in data["features"]:
            for story in feature["stories"]:
                milestone = story.get("milestone") or feature.get("milestone") or data["milestone"]
                s = Story(story, feature["id"], data["id"], milestone, where)
                if s.id in backlog.stories:
                    report.error(where, f"duplicate story id {s.id} (also in {backlog.stories[s.id].file})")
                    continue
                backlog.stories[s.id] = s
    backlog.epics.sort(key=lambda e: e["id"])
    return backlog


def _find_cycles(stories: dict[str, Story]) -> list[list[str]]:
    white, grey, black = 0, 1, 2
    color = dict.fromkeys(stories, white)
    cycles: list[list[str]] = []
    stack: list[str] = []

    def visit(node: str) -> None:
        color[node] = grey
        stack.append(node)
        for dep in sorted(stories[node].depends_on):
            if dep not in stories:
                continue
            if color[dep] == grey:
                cycles.append([*stack[stack.index(dep) :], dep])
            elif color[dep] == white:
                visit(dep)
        stack.pop()
        color[node] = black

    for node in sorted(stories):
        if color[node] == white:
            visit(node)
    return cycles


def _doc_path_exists(root: Path, entry: str) -> bool:
    return (root / entry.split("#", 1)[0]).exists()


def validate(root: Path) -> tuple[Backlog, Report]:
    report = Report()
    backlog = load_backlog(root, report)
    milestone_ids = {m.get("id") for m in backlog.milestones}
    refs_defined = defined_refs(root)
    ids_seen: dict[str, str] = {}

    def check_common(where: str, item: dict[str, Any]) -> None:
        for doc in item.get("docs", []):
            if not _doc_path_exists(root, doc):
                report.error(where, f"docs path does not exist: {doc}")
        for ref in item.get("refs", []):
            if ref not in refs_defined:
                report.error(where, f"ref {ref} is not defined anywhere in docs/")
        milestone = item.get("milestone")
        if milestone and milestone not in milestone_ids:
            report.error(where, f"unknown milestone {milestone}")

    def claim(item_id: str, where: str) -> None:
        if item_id in ids_seen and ids_seen[item_id] != where:
            report.error(where, f"duplicate id {item_id} (also in {ids_seen[item_id]})")
        ids_seen.setdefault(item_id, where)

    for epic in backlog.epics:
        where = backlog.epic_files[epic["id"]]
        claim(epic["id"], where)
        check_common(f"{where} {epic['id']}", epic)
        epic_num = epic["id"][3:]
        for feature in epic["features"]:
            fw = f"{where} {feature['id']}"
            claim(feature["id"], where)
            check_common(fw, feature)
            if not feature["id"].startswith(f"FE-{epic_num}."):
                report.error(fw, f"feature id must start with FE-{epic_num}.")
            feature_num = feature["id"][3:]
            for story in feature["stories"]:
                sw = f"{where} {story['id']}"
                check_common(sw, story)
                if not story["id"].startswith(f"ST-{feature_num}."):
                    report.error(sw, f"story id must start with ST-{feature_num}.")
                if story["status"] == "ready":
                    if story["size"] not in READY_MAX_SIZES:
                        report.error(sw, f"ready stories must be XS, S or M (is {story['size']}); split it")
                    if not story.get("docs"):
                        report.error(sw, "ready stories must link governing docs")

    for story in backlog.stories.values():
        sw = f"{story.file} {story.id}"
        for dep in story.depends_on:
            if dep == story.id:
                report.error(sw, "depends on itself")
            elif dep not in backlog.stories:
                report.error(sw, f"depends_on {dep} does not exist")
            elif story.status == "done" and backlog.stories[dep].status not in FINISHED:
                report.error(sw, f"is done but its dependency {dep} is {backlog.stories[dep].status}")

    for cycle in _find_cycles(backlog.stories):
        report.error("backlog", "dependency cycle: " + " -> ".join(cycle))

    known = set(ids_seen) | set(backlog.stories)
    for path in _reference_files(root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for found in sorted(set(BACKLOG_ID_PATTERN.findall(text))):
            if found not in known:
                report.error(rel(path, root), f"references {found}, which is not in the backlog")

    return backlog, report


def _reference_files(root: Path) -> list[Path]:
    files = [root / f for f in REFERENCE_SCAN_FILES if (root / f).exists()]
    for d in REFERENCE_SCAN_DIRS:
        if (root / d).is_dir():
            files.extend(iter_files(root / d, (".md", ".yaml", ".yml", ".json", ".mdc")))
    rules = root / ".cursor" / "rules"
    if rules.is_dir():
        files.extend(iter_files(rules, (".mdc",)))
    tests_dir = root / "tools" / "tests"
    return [f for f in files if tests_dir not in f.parents]


def _sort_key(story: Story) -> tuple[str, int, list[int]]:
    numbers = [int(n) for n in story.id[3:].split(".")]
    return (story.milestone, PRIORITY_ORDER[story.data["priority"]], numbers)


def next_stories(backlog: Backlog) -> list[Story]:
    out = []
    for story in backlog.stories.values():
        if story.status != "ready":
            continue
        deps = [backlog.stories.get(d) for d in story.depends_on]
        if all(d is not None and d.status == "done" for d in deps):
            out.append(story)
    return sorted(out, key=_sort_key)


def _md(text: str) -> str:
    return " ".join(str(text).split()).replace("|", "\\|")


def render_index(backlog: Backlog) -> str:
    lines = [
        "# Backlog index",
        "",
        "<!-- GENERATED by `make backlog-index` from backlog/epics/*.yaml. Do not edit by hand. -->",
        "",
        "Source of truth: [`backlog/epics/`](epics/). Format and rules: [README.md](README.md).",
        "",
        "## Milestones",
        "",
        "| Milestone | Title | Stories | Done | In progress | Ready | Draft or blocked |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for m in backlog.milestones:
        stories = [s for s in backlog.stories.values() if s.milestone == m["id"]]
        counts = {k: sum(1 for s in stories if s.status == k) for k in ("done", "in-progress", "ready")}
        other = len(stories) - sum(counts.values())
        lines.append(
            f"| {m['id']} | {_md(m['title'])} | {len(stories)} | {counts['done']} | "
            f"{counts['in-progress']} | {counts['ready']} | {other} |"
        )

    lines += [
        "",
        "## Epics",
        "",
        "| Epic | Title | Milestone | Priority | Status | Stories done |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for epic in backlog.epics:
        stories = backlog.epic_stories(epic["id"])
        done = sum(1 for s in stories if s.status == "done")
        file_name = Path(backlog.epic_files[epic["id"]]).name
        lines.append(
            f"| [{epic['id']}](epics/{file_name}) | {_md(epic['title'])} | {epic['milestone']} | "
            f"{epic['priority']} | {derived_status(stories)} | {done}/{len(stories)} |"
        )

    ready = next_stories(backlog)
    lines += ["", "## Ready to start", ""]
    if ready:
        lines += ["| Story | Title | Milestone | Priority | Size |", "| --- | --- | --- | --- | --- |"]
        for s in ready:
            lines.append(
                f"| {s.id} | {_md(s.data['title'])} | {s.milestone} | {s.data['priority']} | {s.data['size']} |"
            )
    else:
        lines.append("No stories are ready with all dependencies done.")

    for epic in backlog.epics:
        file_name = Path(backlog.epic_files[epic["id"]]).name
        lines += ["", f"## {epic['id']}: {_md(epic['title'])}", "", _md(epic["summary"]), ""]
        lines.append(f"File: [`epics/{file_name}`](epics/{file_name})")
        for feature in epic["features"]:
            fstories = backlog.feature_stories(feature["id"])
            lines += [
                "",
                f"### {feature['id']}: {_md(feature['title'])} ({derived_status(fstories)})",
                "",
                "| Story | Title | Type | Status | Priority | Size | Milestone | Depends on |",
                "| --- | --- | --- | --- | --- | --- | --- | --- |",
            ]
            for s in fstories:
                deps = ", ".join(s.depends_on) or "-"
                lines.append(
                    f"| {s.id} | {_md(s.data['title'])} | {s.data['type']} | {s.status} | "
                    f"{s.data['priority']} | {s.data['size']} | {s.milestone} | {deps} |"
                )
    return "\n".join(lines) + "\n"


def story_summary(story: Story) -> dict[str, Any]:
    return {
        "id": story.id,
        "title": story.data["title"],
        "epic": story.epic_id,
        "feature": story.feature_id,
        "milestone": story.milestone,
        "priority": story.data["priority"],
        "size": story.data["size"],
        "type": story.data["type"],
        "file": story.file,
        "docs": story.data.get("docs", []),
        "refs": story.data.get("refs", []),
    }
