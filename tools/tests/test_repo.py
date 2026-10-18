"""Integration checks against the real repository content."""

from __future__ import annotations

from conftest import REAL_ROOT

from warroom_tools import backlog, docs_check, ops_validate


def test_real_backlog_is_valid():
    b, report = backlog.validate(REAL_ROOT)
    assert report.ok, "\n".join(report.errors)
    assert len(b.epics) == 26


def test_real_index_is_fresh():
    b, _ = backlog.validate(REAL_ROOT)
    assert (REAL_ROOT / "backlog" / "INDEX.md").read_text(encoding="utf-8") == backlog.render_index(b)


def test_real_docs_pass():
    report = docs_check.check(REAL_ROOT)
    assert report.ok, "\n".join(report.errors)


def test_real_manifests_pass():
    report = ops_validate.validate(REAL_ROOT)
    assert report.ok, "\n".join(report.errors)
