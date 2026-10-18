from __future__ import annotations

import shutil
import textwrap
from pathlib import Path

import pytest
import yaml

REAL_ROOT = Path(__file__).resolve().parents[2]


def write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip("\n"), encoding="utf-8")
    return path


def doc(title: str, body: str = "", related: str = "[]", reviewed: str = "2026-10-18") -> str:
    return (
        f"---\ntitle: {title}\nstatus: draft\nowner: test\nlast_reviewed: {reviewed}\nrelated: {related}\n---\n\n"
        f"# {title}\n\n{body}\n"
    )


def story(sid: str, **overrides) -> dict:
    data = {
        "id": sid,
        "title": f"Story {sid}",
        "type": "feature",
        "status": "ready",
        "priority": "P1",
        "size": "S",
        "story": "As a tester, I want a story, so that tests have data.",
        "acceptance_criteria": ["Given a fixture, when validated, then it passes."],
        "docs": ["docs/guide.md"],
    }
    data.update(overrides)
    return data


def epic(eid: str, stories: list[dict], milestone: str = "M0") -> dict:
    num = eid[3:]
    return {
        "id": eid,
        "title": f"Epic {eid}",
        "milestone": milestone,
        "priority": "P0",
        "summary": "A fixture epic used by the tooling tests.",
        "features": [{"id": f"FE-{num}.1", "title": "Feature one", "summary": "Fixture feature.", "stories": stories}],
    }


class FixtureRepo:
    def __init__(self, root: Path):
        self.root = root

    def write_epic(self, data: dict, slug: str = "fixture") -> Path:
        path = self.root / "backlog" / "epics" / f"{data['id']}-{slug}.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        return path

    def write(self, rel: str, content: str) -> Path:
        return write(self.root / rel, content)


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> FixtureRepo:
    root = tmp_path / "repo"
    (root / "backlog" / "schema").mkdir(parents=True)
    shutil.copy(REAL_ROOT / "backlog" / "schema" / "backlog.schema.json", root / "backlog" / "schema")
    shutil.copy(REAL_ROOT / "backlog" / "milestones.yaml", root / "backlog")
    (root / "backlog" / "epics").mkdir()
    write(root / "AGENTS.md", "# Agents\n")
    write(
        root / "docs" / "README.md",
        doc("Index", "- [Guide](guide.md)\n- [ADR](adr/0001-first.md)\n- [Access](06-environments/access.md)"),
    )
    write(root / "docs" / "guide.md", doc("Guide", "Rule GDD-TEST-001 is defined here."))
    write(root / "docs" / "adr" / "0001-first.md", doc('"ADR-0001: First"'))
    write(root / "docs" / "06-environments" / "access.md", doc("Access"))
    env_dir = root / "ops" / "environments"
    env_dir.mkdir(parents=True)
    shutil.copy(REAL_ROOT / "ops" / "environments" / "schema.json", env_dir)
    for f in (REAL_ROOT / "ops" / "environments").glob("*.yaml"):
        data = yaml.safe_load(f.read_text(encoding="utf-8"))
        data.pop("created_by_story", None)
        data["runbooks"] = ["docs/06-environments/access.md"]
        (env_dir / f.name).write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    monkeypatch.setenv("WR_REPO_ROOT", str(root))
    return FixtureRepo(root)
