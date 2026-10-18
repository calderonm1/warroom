from __future__ import annotations

import yaml

from warroom_tools import ops_validate


def _edit(repo, name: str, mutate) -> None:
    path = repo.root / "ops" / "environments" / f"{name}.yaml"
    data = yaml.safe_load(path.read_text())
    mutate(data)
    path.write_text(yaml.safe_dump(data))


def test_real_manifests_pass(repo):
    assert ops_validate.validate(repo.root).errors == []


def test_prod_must_not_allow_agent_writes(repo):
    _edit(repo, "prod", lambda d: d["agent_policy"].update(can_deploy=True))
    assert any("can_deploy must be false in prod" in e for e in ops_validate.validate(repo.root).errors)


def test_active_env_rejects_tbd(repo):
    _edit(repo, "dev", lambda d: d.update(status="active"))
    errs = ops_validate.validate(repo.root).errors
    assert any("TBD endpoint" in e for e in errs)
    assert any("real aws.account_id" in e for e in errs)


def test_missing_manifest(repo):
    (repo.root / "ops" / "environments" / "staging.yaml").unlink()
    assert any("'staging'" in e for e in ops_validate.validate(repo.root).errors)


def test_name_must_match_file(repo):
    _edit(repo, "dev", lambda d: d.update(name="staging"))
    assert any("must match file name" in e for e in ops_validate.validate(repo.root).errors)
