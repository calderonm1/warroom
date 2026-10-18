from __future__ import annotations

from conftest import epic, story

from warroom_tools import backlog


def errors_for(repo) -> list[str]:
    _, report = backlog.validate(repo.root)
    return report.errors


def test_valid_backlog_passes(repo):
    repo.write_epic(epic("EP-01", [story("ST-01.1.1", refs=["GDD-TEST-001", "ADR-0001"])]))
    assert errors_for(repo) == []


def test_schema_error_reports_location(repo):
    repo.write_epic(epic("EP-01", [story("ST-01.1.1", size="HUGE")]))
    errs = errors_for(repo)
    assert any("schema: features/0/stories/0/size" in e for e in errs)


def test_file_name_must_match_epic_id(repo):
    repo.write_epic(epic("EP-01", [story("ST-01.1.1")]))
    (repo.root / "backlog/epics/EP-01-fixture.yaml").rename(repo.root / "backlog/epics/EP-02-fixture.yaml")
    assert any("does not match epic id" in e for e in errors_for(repo))


def test_story_prefix_must_match_feature(repo):
    repo.write_epic(epic("EP-01", [story("ST-02.1.1")]))
    assert any("must start with ST-01.1." in e for e in errors_for(repo))


def test_duplicate_story_ids(repo):
    repo.write_epic(epic("EP-01", [story("ST-01.1.1"), story("ST-01.1.1")]))
    assert any("duplicate story id ST-01.1.1" in e for e in errors_for(repo))


def test_missing_dependency(repo):
    repo.write_epic(epic("EP-01", [story("ST-01.1.1", depends_on=["ST-01.1.9"])]))
    assert any("depends_on ST-01.1.9 does not exist" in e for e in errors_for(repo))


def test_dependency_cycle(repo):
    repo.write_epic(
        epic(
            "EP-01",
            [
                story("ST-01.1.1", depends_on=["ST-01.1.2"]),
                story("ST-01.1.2", depends_on=["ST-01.1.3"]),
                story("ST-01.1.3", depends_on=["ST-01.1.1"]),
            ],
        )
    )
    assert any("dependency cycle" in e for e in errors_for(repo))


def test_ready_story_must_be_small_and_documented(repo):
    repo.write_epic(epic("EP-01", [story("ST-01.1.1", size="L"), story("ST-01.1.2", docs=[])]))
    errs = errors_for(repo)
    assert any("ST-01.1.1" in e and "must be XS, S or M" in e for e in errs)
    assert any("ST-01.1.2" in e and "must link governing docs" in e for e in errs)


def test_draft_story_may_be_large(repo):
    repo.write_epic(epic("EP-01", [story("ST-01.1.1", size="L", status="draft")]))
    assert errors_for(repo) == []


def test_done_story_with_unfinished_dependency(repo):
    repo.write_epic(epic("EP-01", [story("ST-01.1.1"), story("ST-01.1.2", status="done", depends_on=["ST-01.1.1"])]))
    assert any("is done but its dependency ST-01.1.1 is ready" in e for e in errors_for(repo))


def test_unknown_ref_and_missing_doc(repo):
    repo.write_epic(epic("EP-01", [story("ST-01.1.1", refs=["GDD-TEST-999"], docs=["docs/nope.md"])]))
    errs = errors_for(repo)
    assert any("ref GDD-TEST-999 is not defined" in e for e in errs)
    assert any("docs path does not exist: docs/nope.md" in e for e in errs)


def test_doc_anchor_is_allowed(repo):
    repo.write_epic(epic("EP-01", [story("ST-01.1.1", docs=["docs/guide.md#section"])]))
    assert errors_for(repo) == []


def test_docs_mentioning_unknown_story_fail(repo):
    repo.write_epic(epic("EP-01", [story("ST-01.1.1")]))
    repo.write("docs/guide.md", "---\ntitle: G\n---\nSee ST-07.7.7 for details.\n")
    assert any("references ST-07.7.7" in e for e in errors_for(repo))


def test_next_orders_by_milestone_priority_and_id(repo):
    repo.write_epic(
        epic(
            "EP-01",
            [
                story("ST-01.1.1", status="done"),
                story("ST-01.1.2", priority="P2", depends_on=["ST-01.1.1"]),
                story("ST-01.1.10", priority="P0"),
                story("ST-01.1.3", priority="P0"),
                story("ST-01.1.4", depends_on=["ST-01.1.2"]),
                story("ST-01.1.5", milestone="M1", priority="P0"),
            ],
        )
    )
    b, report = backlog.validate(repo.root)
    assert report.ok, report.errors
    assert [s.id for s in backlog.next_stories(b)] == ["ST-01.1.3", "ST-01.1.10", "ST-01.1.2", "ST-01.1.5"]


def test_derived_status():
    def mk(status):
        return backlog.Story({"id": "ST-01.1.1", "status": status}, "FE-01.1", "EP-01", "M0", "f")

    assert backlog.derived_status([mk("done"), mk("cancelled")]) == "done"
    assert backlog.derived_status([mk("done"), mk("ready")]) == "in-progress"
    assert backlog.derived_status([mk("ready"), mk("draft")]) == "ready"
    assert backlog.derived_status([mk("draft")]) == "draft"


def test_index_is_deterministic(repo):
    repo.write_epic(epic("EP-01", [story("ST-01.1.1"), story("ST-01.1.2", status="done", depends_on=[])]))
    b1, _ = backlog.validate(repo.root)
    b2, _ = backlog.validate(repo.root)
    text = backlog.render_index(b1)
    assert text == backlog.render_index(b2)
    assert "| ST-01.1.1 | Story ST-01.1.1 | feature | ready |" in text
    assert "GENERATED" in text
