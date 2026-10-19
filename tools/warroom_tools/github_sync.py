"""One-way sync of the YAML backlog to GitHub Issues and a Projects (v2) board (ADR-0014).

The planning step is pure (``build_desired`` + ``plan``) so it is unit tested without network access.
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

from .backlog import Backlog, Story, derived_status

MARKER = "<!-- warroom-backlog-id: {id} -->"
MARKER_PATTERN = re.compile(r"<!-- warroom-backlog-id: ((?:EP|ST)-[0-9.]+) -->")
SYNC_LABEL = "backlog"
API = "https://api.github.com"

STATUS_OPTIONS = {
    "draft": "Draft",
    "ready": "Ready",
    "in-progress": "In Progress",
    "blocked": "Blocked",
    "done": "Done",
    "cancelled": "Cancelled",
}
TYPE_OPTIONS = {
    "epic": "Epic",
    "feature": "Feature",
    "chore": "Chore",
    "spike": "Spike",
    "docs": "Docs",
    "infra": "Infra",
    "test": "Test",
    "bug": "Bug",
}
# Names avoid GitHub Projects reserved/system fields: built-in "Type" (Issue/PR/Draft)
# and "Milestone" (GitHub issue milestones).
SINGLE_SELECT_FIELDS = ("Status", "Priority", "Size", "Roadmap", "Kind")
TEXT_FIELDS = ("Epic",)


@dataclass(frozen=True)
class DesiredItem:
    backlog_id: str
    kind: str
    title: str
    body: str
    closed: bool
    labels: tuple[str, ...]
    fields: tuple[tuple[str, str], ...]

    @property
    def field_map(self) -> dict[str, str]:
        return dict(self.fields)


@dataclass
class ExistingIssue:
    number: int
    node_id: str
    title: str
    body: str
    state: str
    labels: tuple[str, ...] = ()


@dataclass
class ProjectItem:
    item_id: str
    fields: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Action:
    op: str
    backlog_id: str
    detail: str = ""


def _blob_url(repo: str | None, branch: str, path: str) -> str:
    if not repo:
        return path
    return f"https://github.com/{repo}/blob/{branch}/{path}"


def _story_body(story: Story, backlog: Backlog, repo: str | None, branch: str) -> str:
    d = story.data
    epic = next(e for e in backlog.epics if e["id"] == story.epic_id)
    feature = next(f for f in epic["features"] if f["id"] == story.feature_id)
    done = story.status == "done"
    lines = [
        MARKER.format(id=story.id),
        f"> Generated from [`{story.file}`]({_blob_url(repo, branch, story.file)}). "
        "Edit the YAML in the repo, not this issue.",
        "",
        f"**Epic:** {epic['id']} {epic['title']} | **Feature:** {feature['id']} {feature['title']}",
        "",
        f"**Milestone:** {story.milestone} | **Priority:** {d['priority']} | **Size:** {d['size']} | "
        f"**Type:** {d['type']} | **Status:** {d['status']}",
        "",
        "### Story",
        "",
        " ".join(d["story"].split()),
        "",
        "### Acceptance criteria",
        "",
    ]
    lines += [f"- [{'x' if done else ' '}] {' '.join(ac.split())}" for ac in d["acceptance_criteria"]]
    if d.get("docs"):
        lines += ["", "### Docs", ""]
        lines += [f"- [{p}]({_blob_url(repo, branch, p)})" for p in d["docs"]]
    if d.get("refs"):
        lines += ["", "### Refs", "", ", ".join(d["refs"])]
    if d.get("depends_on"):
        lines += ["", "### Depends on", ""]
        for dep in d["depends_on"]:
            other = backlog.stories.get(dep)
            lines.append(f"- {dep} {other.data['title'] if other else '(missing)'}")
    if d.get("agent_notes"):
        lines += ["", "### Agent notes", "", d["agent_notes"].strip()]
    return "\n".join(lines) + "\n"


def _epic_body(epic: dict[str, Any], backlog: Backlog, repo: str | None, branch: str) -> str:
    file = backlog.epic_files[epic["id"]]
    lines = [
        MARKER.format(id=epic["id"]),
        f"> Generated from [`{file}`]({_blob_url(repo, branch, file)}). Edit the YAML in the repo, not this issue.",
        "",
        f"**Milestone:** {epic['milestone']} | **Priority:** {epic['priority']}",
        "",
        "### Summary",
        "",
        " ".join(epic["summary"].split()),
    ]
    if epic.get("outcome"):
        lines += ["", "### Outcome", "", " ".join(epic["outcome"].split())]
    for feature in epic["features"]:
        lines += ["", f"### {feature['id']} {feature['title']}", ""]
        for s in feature["stories"]:
            mark = "x" if s["status"] == "done" else " "
            lines.append(f"- [{mark}] {s['id']} {s['title']} ({s['status']})")
    return "\n".join(lines) + "\n"


def build_desired(backlog: Backlog, repo: str | None = None, branch: str = "main") -> list[DesiredItem]:
    items: list[DesiredItem] = []
    for epic in backlog.epics:
        status = derived_status(backlog.epic_stories(epic["id"]))
        items.append(
            DesiredItem(
                backlog_id=epic["id"],
                kind="epic",
                title=f"[{epic['id']}] {epic['title']}",
                body=_epic_body(epic, backlog, repo, branch),
                closed=status == "done",
                labels=(SYNC_LABEL, "kind-epic"),
                fields=(
                    ("Status", STATUS_OPTIONS[status]),
                    ("Priority", epic["priority"]),
                    ("Roadmap", epic["milestone"]),
                    ("Kind", TYPE_OPTIONS["epic"]),
                    ("Epic", epic["id"]),
                ),
            )
        )
    for story in sorted(backlog.stories.values(), key=lambda s: [int(n) for n in s.id[3:].split(".")]):
        d = story.data
        items.append(
            DesiredItem(
                backlog_id=story.id,
                kind="story",
                title=f"[{story.id}] {d['title']}",
                body=_story_body(story, backlog, repo, branch),
                closed=story.status in {"done", "cancelled"},
                labels=(SYNC_LABEL, "kind-story"),
                fields=(
                    ("Status", STATUS_OPTIONS[story.status]),
                    ("Priority", d["priority"]),
                    ("Size", d["size"]),
                    ("Roadmap", story.milestone),
                    ("Kind", TYPE_OPTIONS[d["type"]]),
                    ("Epic", story.epic_id),
                ),
            )
        )
    return items


def parse_marker(body: str | None) -> str | None:
    match = MARKER_PATTERN.search(body or "")
    return match.group(1) if match else None


def plan(
    desired: list[DesiredItem],
    issues: dict[str, ExistingIssue],
    project_items: dict[str, ProjectItem],
) -> list[Action]:
    """Compute the actions needed to make GitHub match the backlog. Keys of ``issues`` are backlog IDs;
    keys of ``project_items`` are issue node IDs."""
    actions: list[Action] = []
    for item in desired:
        issue = issues.get(item.backlog_id)
        if issue is None:
            actions.append(Action("create_issue", item.backlog_id, item.title))
            actions.append(Action("add_to_project", item.backlog_id))
            for name, value in item.fields:
                actions.append(Action("set_field", item.backlog_id, f"{name}={value}"))
            continue
        want_state = "closed" if item.closed else "open"
        changes = []
        if issue.title != item.title:
            changes.append("title")
        if (issue.body or "").replace("\r\n", "\n").strip() != item.body.strip():
            changes.append("body")
        if issue.state != want_state:
            changes.append(f"state->{want_state}")
        if changes:
            actions.append(Action("update_issue", item.backlog_id, ",".join(changes)))
        project_item = project_items.get(issue.node_id)
        if project_item is None:
            actions.append(Action("add_to_project", item.backlog_id))
            current: dict[str, str] = {}
        else:
            current = project_item.fields
        for name, value in item.fields:
            if current.get(name) != value:
                actions.append(Action("set_field", item.backlog_id, f"{name}={value}"))
    return actions


def summarize(actions: list[Action]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for a in actions:
        counts[a.op] = counts.get(a.op, 0) + 1
    return dict(sorted(counts.items()))


class GitHubError(RuntimeError):
    pass


class GitHubClient:
    def __init__(self, token: str, repo: str):
        self.token = token
        self.repo = repo

    def _request(self, method: str, url: str, payload: dict[str, Any] | None = None) -> Any:
        data = json.dumps(payload).encode() if payload is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        if data is not None:
            req.add_header("Content-Type", "application/json")
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    raw = resp.read()
                    return json.loads(raw) if raw else None
            except urllib.error.HTTPError as exc:
                body = exc.read().decode(errors="replace")
                if exc.code in (403, 429, 502, 503) and attempt < 3:
                    time.sleep(2 ** (attempt + 2))
                    continue
                raise GitHubError(f"{method} {url} -> {exc.code}: {body}") from exc
        raise GitHubError(f"{method} {url} failed after retries")

    def graphql(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        result = self._request("POST", f"{API}/graphql", {"query": query, "variables": variables})
        if result.get("errors"):
            raise GitHubError(json.dumps(result["errors"]))
        return result["data"]

    def ensure_labels(self, labels: set[str]) -> None:
        for name in sorted(labels):
            try:
                self._request("POST", f"{API}/repos/{self.repo}/labels", {"name": name, "color": "5319e7"})
            except GitHubError as exc:
                if "already_exists" not in str(exc):
                    raise

    def list_issues(self) -> dict[str, ExistingIssue]:
        out: dict[str, ExistingIssue] = {}
        page = 1
        while True:
            url = f"{API}/repos/{self.repo}/issues?state=all&labels={SYNC_LABEL}&per_page=100&page={page}"
            batch = self._request("GET", url) or []
            for issue in batch:
                if "pull_request" in issue:
                    continue
                backlog_id = parse_marker(issue.get("body"))
                if backlog_id:
                    out[backlog_id] = ExistingIssue(
                        number=issue["number"],
                        node_id=issue["node_id"],
                        title=issue["title"],
                        body=issue.get("body") or "",
                        state=issue["state"],
                        labels=tuple(lbl["name"] for lbl in issue.get("labels", [])),
                    )
            if len(batch) < 100:
                return out
            page += 1

    def create_issue(self, item: DesiredItem) -> ExistingIssue:
        issue = self._request(
            "POST",
            f"{API}/repos/{self.repo}/issues",
            {"title": item.title, "body": item.body, "labels": list(item.labels)},
        )
        if item.closed:
            self._request("PATCH", f"{API}/repos/{self.repo}/issues/{issue['number']}", {"state": "closed"})
        return ExistingIssue(issue["number"], issue["node_id"], item.title, item.body, "open")

    def update_issue(self, number: int, item: DesiredItem) -> None:
        self._request(
            "PATCH",
            f"{API}/repos/{self.repo}/issues/{number}",
            {
                "title": item.title,
                "body": item.body,
                "state": "closed" if item.closed else "open",
                "labels": list(item.labels),
            },
        )


PROJECT_QUERY = """
query($owner: String!, $number: Int!) {
  %s(login: $owner) {
    projectV2(number: $number) {
      id
      fields(first: 50) {
        nodes {
          ... on ProjectV2FieldCommon { id name dataType }
          ... on ProjectV2SingleSelectField { id name options { id name } }
        }
      }
    }
  }
}
"""

ITEMS_QUERY = """
query($id: ID!, $after: String) {
  node(id: $id) {
    ... on ProjectV2 {
      items(first: 100, after: $after) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          content { ... on Issue { id } }
          fieldValues(first: 20) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue { name field { ... on ProjectV2FieldCommon { name } } }
              ... on ProjectV2ItemFieldTextValue { text field { ... on ProjectV2FieldCommon { name } } }
            }
          }
        }
      }
    }
  }
}
"""

ADD_ITEM = """
mutation($project: ID!, $content: ID!) {
  addProjectV2ItemById(input: {projectId: $project, contentId: $content}) { item { id } }
}
"""

ISSUE_PROJECT_ITEMS = """
query($id: ID!) {
  node(id: $id) {
    ... on Issue {
      projectItems(first: 50) {
        nodes { id project { id } }
      }
    }
  }
}
"""

ALREADY_IN_PROJECT = "Content already exists in this project"

SET_SELECT = """
mutation($project: ID!, $item: ID!, $field: ID!, $option: String!) {
  updateProjectV2ItemFieldValue(input: {projectId: $project, itemId: $item, fieldId: $field,
    value: {singleSelectOptionId: $option}}) { projectV2Item { id } }
}
"""

SET_TEXT = """
mutation($project: ID!, $item: ID!, $field: ID!, $text: String!) {
  updateProjectV2ItemFieldValue(input: {projectId: $project, itemId: $item, fieldId: $field,
    value: {text: $text}}) { projectV2Item { id } }
}
"""


@dataclass
class Project:
    id: str
    fields: dict[str, dict[str, Any]]


def load_project(client: GitHubClient, owner: str, number: int) -> Project:
    last_error: Exception | None = None
    for owner_type in ("organization", "user"):
        try:
            data = client.graphql(PROJECT_QUERY % owner_type, {"owner": owner, "number": number})
        except GitHubError as exc:
            last_error = exc
            continue
        node = (data.get(owner_type) or {}).get("projectV2")
        if node:
            fields = {}
            for f in node["fields"]["nodes"]:
                if not f:
                    continue
                options = {o["name"]: o["id"] for o in f.get("options", [])}
                fields[f["name"]] = {"id": f["id"], "options": options}
            return Project(node["id"], fields)
    raise GitHubError(f"project {owner}#{number} not found: {last_error}")


def check_project_fields(project: Project, desired: list[DesiredItem]) -> list[str]:
    problems = []
    for name in (*SINGLE_SELECT_FIELDS, *TEXT_FIELDS):
        if name not in project.fields:
            problems.append(f"project is missing field '{name}'")
    for item in desired:
        for name, value in item.fields:
            if name in SINGLE_SELECT_FIELDS and name in project.fields and value not in project.fields[name]["options"]:
                problems.append(f"field '{name}' is missing option '{value}'")
    return sorted(set(problems))


def load_project_items(client: GitHubClient, project: Project) -> dict[str, ProjectItem]:
    out: dict[str, ProjectItem] = {}
    after = None
    while True:
        data = client.graphql(ITEMS_QUERY, {"id": project.id, "after": after})
        items = data["node"]["items"]
        for node in items["nodes"]:
            content = node.get("content") or {}
            if not content.get("id"):
                continue
            values = {}
            for fv in node["fieldValues"]["nodes"]:
                if not fv or not fv.get("field"):
                    continue
                values[fv["field"]["name"]] = fv.get("name") if "name" in fv else fv.get("text")
            out[content["id"]] = ProjectItem(node["id"], values)
        if not items["pageInfo"]["hasNextPage"]:
            return out
        after = items["pageInfo"]["endCursor"]


def is_already_in_project(exc: BaseException) -> bool:
    return ALREADY_IN_PROJECT in str(exc)


def find_project_item_id(client: GitHubClient, project_id: str, content_id: str) -> str | None:
    data = client.graphql(ISSUE_PROJECT_ITEMS, {"id": content_id})
    nodes = ((data.get("node") or {}).get("projectItems") or {}).get("nodes") or []
    for node in nodes:
        if node and (node.get("project") or {}).get("id") == project_id:
            return node["id"]
    return None


def add_or_find_project_item(client: GitHubClient, project: Project, content_id: str) -> str:
    """Add content to the project, or return the existing item id if GitHub already has it.

    Project auto-add workflows (and a previous partial sync) can win the race after
    ``create_issue``. ``addProjectV2ItemById`` then returns UNPROCESSABLE instead of the item.
    """
    try:
        data = client.graphql(ADD_ITEM, {"project": project.id, "content": content_id})
        return data["addProjectV2ItemById"]["item"]["id"]
    except GitHubError as exc:
        if not is_already_in_project(exc):
            raise
        item_id = find_project_item_id(client, project.id, content_id)
        if item_id is None:
            raise GitHubError(
                f"content {content_id} is already in project {project.id} but its item id could not be loaded"
            ) from exc
        return item_id


def apply(
    client: GitHubClient,
    project: Project,
    desired: list[DesiredItem],
    issues: dict[str, ExistingIssue],
    project_items: dict[str, ProjectItem],
) -> list[Action]:
    done: list[Action] = []
    client.ensure_labels({lbl for item in desired for lbl in item.labels})
    for item in desired:
        item_actions = plan([item], issues, project_items)
        if not item_actions:
            continue
        issue = issues.get(item.backlog_id)
        for action in item_actions:
            if action.op == "create_issue":
                issue = client.create_issue(item)
                issues[item.backlog_id] = issue
                time.sleep(1)
            elif action.op == "update_issue" and issue is not None:
                client.update_issue(issue.number, item)
            elif action.op == "add_to_project" and issue is not None:
                item_id = add_or_find_project_item(client, project, issue.node_id)
                project_items[issue.node_id] = ProjectItem(item_id)
            elif action.op == "set_field" and issue is not None:
                name, value = action.detail.split("=", 1)
                meta = project.fields[name]
                item_id = project_items[issue.node_id].item_id
                if name in TEXT_FIELDS:
                    client.graphql(
                        SET_TEXT, {"project": project.id, "item": item_id, "field": meta["id"], "text": value}
                    )
                else:
                    client.graphql(
                        SET_SELECT,
                        {
                            "project": project.id,
                            "item": item_id,
                            "field": meta["id"],
                            "option": meta["options"][value],
                        },
                    )
                project_items[issue.node_id].fields[name] = value
            done.append(action)
    return done


def env_config() -> dict[str, str | None]:
    return {
        "token": os.environ.get("WR_PROJECTS_TOKEN") or os.environ.get("GITHUB_TOKEN"),
        "repo": os.environ.get("GITHUB_REPOSITORY"),
        "owner": os.environ.get("WR_PROJECT_OWNER"),
        "number": os.environ.get("WR_PROJECT_NUMBER"),
    }
