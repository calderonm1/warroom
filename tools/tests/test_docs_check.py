from __future__ import annotations

import datetime as dt

from conftest import doc

from warroom_tools import docs_check


def test_fixture_docs_pass(repo):
    assert docs_check.check(repo.root).errors == []


def test_missing_front_matter(repo):
    repo.write("docs/guide.md", "# Guide\n")
    assert any("missing YAML front matter" in e for e in docs_check.check(repo.root).errors)


def test_invalid_front_matter_yaml_is_reported(repo):
    repo.write("docs/guide.md", doc("Bad: title"))
    assert any("front matter is not valid YAML" in e for e in docs_check.check(repo.root).errors)


def test_missing_key_and_bad_status(repo):
    repo.write("docs/guide.md", "---\ntitle: G\nstatus: wip\nowner: x\nlast_reviewed: 2026-10-18\n---\n")
    errs = docs_check.check(repo.root).errors
    assert any("missing 'related'" in e for e in errs)
    assert any("status 'wip'" in e for e in errs)


def test_broken_link_and_code_blocks_ignored(repo):
    body = "[ok](adr/0001-first.md) [bad](missing.md) `[code](nope.md)`\n\n```\n[fenced](nope2.md)\n```\n"
    repo.write("docs/guide.md", doc("Guide", body))
    errs = docs_check.check(repo.root).errors
    assert any("broken link: missing.md" in e for e in errs)
    assert not any("nope" in e for e in errs)


def test_external_and_anchor_links_ignored(repo):
    repo.write("docs/guide.md", doc("Guide", "[a](https://example.com) [b](#top) [c](adr/0001-first.md#x)"))
    assert docs_check.check(repo.root).errors == []


def test_unindexed_doc(repo):
    repo.write("docs/orphan.md", doc("Orphan"))
    assert any("docs/orphan.md: not linked from docs/README.md" in e for e in docs_check.check(repo.root).errors)


def test_related_paths_and_adrs(repo):
    repo.write("docs/guide.md", doc("Guide", related="[ADR-0001, ADR-0042, docs/nope.md, EP-01]"))
    errs = docs_check.check(repo.root).errors
    assert any("related ADR-0042 has no ADR file" in e for e in errs)
    assert any("related path does not exist: docs/nope.md" in e for e in errs)
    assert not any("ADR-0001" in e or "EP-01" in e for e in errs)


def test_template_skips_date_check(repo):
    repo.write("docs/adr/0000-template.md", doc("Template", reviewed="YYYY-MM-DD", related="[docs/missing.md]"))
    index = "[g](guide.md) [a](adr/0001-first.md) [t](adr/0000-template.md) [x](06-environments/access.md)"
    repo.write("docs/README.md", doc("Index", index))
    assert docs_check.check(repo.root).errors == []


def test_stale_docs(repo):
    repo.write("docs/guide.md", doc("Guide", reviewed="2025-01-01"))
    rows = docs_check.stale(repo.root, days=180, today=dt.date(2026, 10, 18))
    assert [r[0] for r in rows] == ["docs/guide.md"]
    assert docs_check.stale(repo.root, days=1000, today=dt.date(2026, 10, 18)) == []
