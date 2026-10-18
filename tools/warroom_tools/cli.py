"""`wr` command line: repo tooling for humans, CI and AI agents.

Every command exits non-zero on failure and supports machine-readable output where useful.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from . import backlog as backlog_mod
from . import docs_check, github_sync, ops_validate
from .common import repo_root


def _cmd_backlog_validate(root: Path, args: argparse.Namespace) -> int:
    backlog, report = backlog_mod.validate(root)
    report.print("backlog-validate")
    if report.ok:
        print(f"{len(backlog.epics)} epics, {len(backlog.stories)} stories")
    return 0 if report.ok else 1


def _cmd_backlog_index(root: Path, args: argparse.Namespace) -> int:
    backlog, report = backlog_mod.validate(root)
    if not report.ok:
        report.print("backlog-validate")
        return 1
    content = backlog_mod.render_index(backlog)
    path = root / "backlog" / "INDEX.md"
    if args.check:
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        if current != content:
            print("backlog/INDEX.md is stale. Run `make backlog-index` and commit the result.")
            return 1
        print("backlog/INDEX.md is up to date")
        return 0
    path.write_text(content, encoding="utf-8")
    print(f"wrote {path.relative_to(root)}")
    return 0


def _cmd_backlog_next(root: Path, args: argparse.Namespace) -> int:
    backlog, report = backlog_mod.validate(root)
    if not report.ok:
        report.print("backlog-validate")
        return 1
    stories = backlog_mod.next_stories(backlog)
    if args.milestone:
        stories = [s for s in stories if s.milestone == args.milestone]
    stories = stories[: args.limit] if args.limit else stories
    if args.json:
        print(json.dumps([backlog_mod.story_summary(s) for s in stories], indent=2))
        return 0
    if not stories:
        print("No ready stories with all dependencies done.")
        return 0
    print(f"{'ID':<12} {'MS':<3} {'PRI':<3} {'SIZE':<4} TITLE")
    for s in stories:
        print(f"{s.id:<12} {s.milestone:<3} {s.data['priority']:<3} {s.data['size']:<4} {s.data['title']}")
    return 0


def _cmd_backlog_sync(root: Path, args: argparse.Namespace) -> int:
    backlog, report = backlog_mod.validate(root)
    if not report.ok:
        report.print("backlog-validate")
        return 1
    cfg = github_sync.env_config()
    repo = args.repo or cfg["repo"]
    owner = args.owner or cfg["owner"]
    number = args.project_number or cfg["number"]
    desired = github_sync.build_desired(backlog, repo=repo, branch=args.branch)

    if not cfg["token"] or not repo or not owner or not number:
        if args.apply:
            print("Missing configuration: set GITHUB_TOKEN (or WR_PROJECTS_TOKEN), GITHUB_REPOSITORY,")
            print("WR_PROJECT_OWNER and WR_PROJECT_NUMBER. See tools/README.md.")
            return 2
        offline = github_sync.plan(desired, {}, {})
        print("Offline plan (no GitHub credentials or project configured): assuming nothing exists yet.")
        print(json.dumps({"items": len(desired), "actions": github_sync.summarize(offline)}, indent=2))
        return 0

    client = github_sync.GitHubClient(cfg["token"], repo)
    project = github_sync.load_project(client, owner, int(number))
    problems = github_sync.check_project_fields(project, desired)
    if problems:
        for p in problems:
            print(f"ERROR project: {p}")
        print("Add the missing fields or options to the project (tools/README.md lists them).")
        return 1
    issues = client.list_issues()
    items = github_sync.load_project_items(client, project)
    actions = github_sync.plan(desired, issues, items)
    print(json.dumps({"items": len(desired), "actions": github_sync.summarize(actions)}, indent=2))
    if args.verbose:
        for a in actions:
            print(f"{a.op:<15} {a.backlog_id:<12} {a.detail}")
    if not args.apply:
        print("Dry run. Re-run with --apply to make these changes.")
        return 0
    done = github_sync.apply(client, project, desired, issues, items)
    print(f"Applied {len(done)} actions.")
    return 0


def _cmd_docs_check(root: Path, args: argparse.Namespace) -> int:
    report = docs_check.check(root)
    report.print("docs-check")
    return 0 if report.ok else 1


def _cmd_docs_stale(root: Path, args: argparse.Namespace) -> int:
    today = dt.date.fromisoformat(args.today) if args.today else None
    rows = docs_check.stale(root, args.days, today)
    if args.json:
        print(json.dumps([{"path": p, "last_reviewed": d.isoformat(), "age_days": a} for p, d, a in rows], indent=2))
        return 0
    if not rows:
        print(f"No docs older than {args.days} days.")
        return 0
    for path, reviewed, age in rows:
        print(f"{age:>5} days  {reviewed.isoformat()}  {path}")
    return 0


def _cmd_ops_validate(root: Path, args: argparse.Namespace) -> int:
    report = ops_validate.validate(root)
    report.print("ops-validate")
    return 0 if report.ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wr", description="War Room repo tooling")
    sub = parser.add_subparsers(dest="group", required=True)

    bl = sub.add_parser("backlog", help="backlog commands").add_subparsers(dest="cmd", required=True)
    bl.add_parser("validate", help="validate backlog YAML").set_defaults(func=_cmd_backlog_validate)
    p = bl.add_parser("index", help="regenerate backlog/INDEX.md")
    p.add_argument("--check", action="store_true", help="fail if INDEX.md is stale instead of writing it")
    p.set_defaults(func=_cmd_backlog_index)
    p = bl.add_parser("next", help="list ready stories whose dependencies are done")
    p.add_argument("--json", action="store_true")
    p.add_argument("--milestone")
    p.add_argument("--limit", type=int, default=0)
    p.set_defaults(func=_cmd_backlog_next)
    p = bl.add_parser("sync-github", help="sync to GitHub Issues and Projects (dry run by default)")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--repo", help="owner/name (default: GITHUB_REPOSITORY)")
    p.add_argument("--owner", help="project owner login (default: WR_PROJECT_OWNER)")
    p.add_argument("--project-number", help="project number (default: WR_PROJECT_NUMBER)")
    p.add_argument("--branch", default="main", help="branch used for links in issue bodies")
    p.add_argument("--verbose", "-v", action="store_true")
    p.set_defaults(func=_cmd_backlog_sync)

    dc = sub.add_parser("docs", help="documentation commands").add_subparsers(dest="cmd", required=True)
    dc.add_parser("check", help="front matter, links and index coverage").set_defaults(func=_cmd_docs_check)
    p = dc.add_parser("stale", help="docs not reviewed recently")
    p.add_argument("--days", type=int, default=180)
    p.add_argument("--today", help="override today's date (YYYY-MM-DD)")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=_cmd_docs_stale)

    op = sub.add_parser("ops", help="environment manifest commands").add_subparsers(dest="cmd", required=True)
    op.add_parser("validate", help="validate ops/environments manifests").set_defaults(func=_cmd_ops_validate)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        root = repo_root()
    except RuntimeError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2
    return args.func(root, args)


if __name__ == "__main__":
    sys.exit(main())
