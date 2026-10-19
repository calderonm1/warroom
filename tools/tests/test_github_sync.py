from __future__ import annotations

import pytest
from conftest import epic, story

from warroom_tools import backlog, github_sync
from warroom_tools.github_sync import ExistingIssue, GitHubError, ProjectItem

EXISTING_ERROR = (
    '[{"type": "UNPROCESSABLE", "path": ["addProjectV2ItemById"], '
    '"locations": [{"line": 3, "column": 3}], '
    '"message": "Content already exists in this project"}]'
)


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


class FakeClient:
    def __init__(self, add_error: str | None = None, items: dict[str, list[tuple[str, str]]] | None = None):
        self.add_error = add_error
        self.items = items or {}
        self.calls: list[tuple[str, dict]] = []
        self.field_updates: list[dict] = []

    def ensure_labels(self, labels: set[str]) -> None:
        pass

    def graphql(self, query: str, variables: dict) -> dict:
        self.calls.append((query, variables))
        if "addProjectV2ItemById" in query:
            if self.add_error:
                raise GitHubError(self.add_error)
            return {"addProjectV2ItemById": {"item": {"id": "PVTI_new"}}}
        if "projectItems" in query:
            nodes = [
                {"id": item_id, "project": {"id": project_id}}
                for project_id, item_id in self.items.get(variables["id"], [])
            ]
            return {"node": {"projectItems": {"nodes": nodes}}}
        if "updateProjectV2ItemFieldValue" in query:
            self.field_updates.append(variables)
            return {"updateProjectV2ItemFieldValue": {"projectV2Item": {"id": variables["item"]}}}
        raise AssertionError(f"unexpected query: {query}")


def _project() -> github_sync.Project:
    return github_sync.Project(
        "P_1",
        {
            "Status": {"id": "f1", "options": {"Ready": "o1", "In Progress": "o2", "Done": "o3"}},
            "Priority": {"id": "f2", "options": {"P0": "p0", "P1": "p1"}},
            "Size": {"id": "f3", "options": {"S": "s"}},
            "Roadmap": {"id": "f4", "options": {"M0": "m0"}},
            "Kind": {"id": "f5", "options": {"Epic": "e", "Feature": "f"}},
            "Epic": {"id": "f6", "options": {}},
        },
    )


def test_add_or_find_project_item_returns_new_id():
    client = FakeClient()
    assert github_sync.add_or_find_project_item(client, _project(), "I_1") == "PVTI_new"


def test_add_or_find_project_item_reuses_existing_on_conflict():
    client = FakeClient(add_error=EXISTING_ERROR, items={"I_1": [("P_1", "PVTI_existing"), ("P_other", "PVTI_other")]})
    assert github_sync.add_or_find_project_item(client, _project(), "I_1") == "PVTI_existing"


def test_add_or_find_project_item_reraises_other_errors():
    client = FakeClient(add_error='[{"message": "Resource not accessible by integration"}]')
    with pytest.raises(GitHubError, match="Resource not accessible"):
        github_sync.add_or_find_project_item(client, _project(), "I_1")


def test_add_or_find_project_item_errors_when_existing_item_missing():
    client = FakeClient(add_error=EXISTING_ERROR, items={"I_1": []})
    with pytest.raises(GitHubError, match="could not be loaded"):
        github_sync.add_or_find_project_item(client, _project(), "I_1")


def test_apply_continues_field_updates_when_item_already_in_project(repo):
    desired = [d for d in _desired(repo) if d.backlog_id == "EP-01"]
    issue = ExistingIssue(5, "I_EP01", desired[0].title, desired[0].body, "open")
    client = FakeClient(add_error=EXISTING_ERROR, items={"I_EP01": [("P_1", "PVTI_existing")]})
    done = github_sync.apply(client, _project(), desired, {"EP-01": issue}, {})
    assert any(a.op == "add_to_project" for a in done)
    assert any(a.op == "set_field" for a in done)
    assert {u["item"] for u in client.field_updates} == {"PVTI_existing"}
