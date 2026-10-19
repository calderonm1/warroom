from __future__ import annotations

from conftest import epic, story

from warroom_tools import backlog, github_sync
from warroom_tools.github_sync import ExistingIssue, ProjectItem


def _desired(repo):
    repo.write_epic(
        epic(
            "EP-01",
            [
                story("ST-01.1.1", status="done"),
                story("ST-01.1.2", depends_on=["ST-01.1.1"], refs=["ADR-0001"]),
            ],
        )
    )
    b, report = backlog.validate(repo.root)
    assert report.ok, report.errors
    return github_sync.build_desired(b, repo="acme/warroom")


def _in_sync(desired):
    issues, items = {}, {}
    for n, d in enumerate(desired, start=1):
        node = f"I_{n}"
        issues[d.backlog_id] = ExistingIssue(n, node, d.title, d.body, "closed" if d.closed else "open")
        items[node] = ProjectItem(f"PVTI_{n}", dict(d.fields))
    return issues, items


def test_build_desired_shapes_items(repo):
    desired = {d.backlog_id: d for d in _desired(repo)}
    assert set(desired) == {"EP-01", "ST-01.1.1", "ST-01.1.2"}
    s = desired["ST-01.1.2"]
    assert s.title == "[ST-01.1.2] Story ST-01.1.2"
    assert github_sync.parse_marker(s.body) == "ST-01.1.2"
    assert "https://github.com/acme/warroom/blob/main/docs/guide.md" in s.body
    assert "- ST-01.1.1 Story ST-01.1.1" in s.body
    assert s.field_map == {
        "Status": "Ready",
        "Priority": "P1",
        "Size": "S",
        "Roadmap": "M0",
        "Kind": "Feature",
        "Epic": "EP-01",
    }
    assert desired["ST-01.1.1"].closed is True
    assert "- [x]" in desired["ST-01.1.1"].body
    assert desired["EP-01"].field_map["Status"] == "In Progress"
    assert desired["EP-01"].closed is False


def test_plan_creates_everything_when_empty(repo):
    desired = _desired(repo)
    summary = github_sync.summarize(github_sync.plan(desired, {}, {}))
    assert summary["create_issue"] == 3
    assert summary["add_to_project"] == 3
    assert summary["set_field"] == sum(len(d.fields) for d in desired)


def test_plan_is_empty_when_in_sync(repo):
    desired = _desired(repo)
    issues, items = _in_sync(desired)
    assert github_sync.plan(desired, issues, items) == []


def test_plan_detects_drift(repo):
    desired = _desired(repo)
    issues, items = _in_sync(desired)
    issues["ST-01.1.2"].title = "edited on GitHub"
    issues["ST-01.1.1"].state = "open"
    issues["ST-01.1.1"].body = issues["ST-01.1.1"].body.replace("\n", "\r\n")
    items[issues["ST-01.1.2"].node_id].fields["Priority"] = "P0"
    del items[issues["EP-01"].node_id]
    actions = {(a.op, a.backlog_id, a.detail) for a in github_sync.plan(desired, issues, items)}
    assert ("update_issue", "ST-01.1.2", "title") in actions
    assert ("update_issue", "ST-01.1.1", "state->closed") in actions
    assert ("set_field", "ST-01.1.2", "Priority=P1") in actions
    assert ("add_to_project", "EP-01", "") in actions
    assert ("set_field", "EP-01", "Kind=Epic") in actions


def test_project_field_check(repo):
    desired = _desired(repo)
    project = github_sync.Project(
        "P",
        {
            "Status": {"id": "f1", "options": {"Ready": "o1", "Done": "o2"}},
            "Priority": {"id": "f2", "options": {"P0": "o", "P1": "o"}},
            "Roadmap": {"id": "f3", "options": {"M0": "o"}},
            "Kind": {"id": "f4", "options": {"Feature": "o", "Epic": "o"}},
            "Epic": {"id": "f5", "options": {}},
        },
    )
    problems = github_sync.check_project_fields(project, desired)
    assert "project is missing field 'Size'" in problems
    assert "field 'Status' is missing option 'In Progress'" in problems


def test_parse_marker():
    assert github_sync.parse_marker("x\n<!-- warroom-backlog-id: ST-05.1.2 -->\n") == "ST-05.1.2"
    assert github_sync.parse_marker("no marker") is None
    assert github_sync.parse_marker(None) is None
