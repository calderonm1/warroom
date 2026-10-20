"""ST-02.1.1: toolchain pins and `wr doctor`."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from conftest import REAL_ROOT

from warroom_tools import cli, doctor

INSTALL = "docs/06-environments/local-development.md#1-workstation-prerequisites"

HAPPY = {
    ("dotnet", "--list-sdks"): (0, "10.0.100 [/sdk]\n10.0.402 [/sdk]\n10.0.500 [/sdk]\n"),
    ("python3", "--version"): (0, "Python 3.12.3\n"),
    ("uv", "--version"): (0, "uv 0.13.2 (x86_64-unknown-linux-gnu)\n"),
    ("docker", "--version"): (0, "Docker version 28.3.2, build abc\n"),
    ("terraform", "version"): (0, "Terraform v1.16.6\non linux_amd64\n"),
    ("git", "lfs", "version"): (0, "git-lfs/3.8.0 (GitHub; linux amd64; go 1.27.0)\n"),
    ("buf", "--version"): (0, "1.74.0\n"),
}


def _write_pins(root: Path, *, unity: str = "6000.3", terraform_file: str = "1.16.6", extra: str = "") -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "global.json").write_text(
        json.dumps(
            {"sdk": {"version": "10.0.402", "rollForward": "latestFeature", "allowPrerelease": False}},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / ".tool-versions").write_text(
        "python 3.12.3\nuv 0.13.2\nterraform 1.16.6\nbuf 1.74.0\n" + extra,
        encoding="utf-8",
    )
    (root / ".terraform-version").write_text(terraform_file + "\n", encoding="utf-8")
    (root / ".unity-version").write_text(unity + "\n", encoding="utf-8")


def _runner(responses: dict[tuple[str, ...], tuple[int, str]]):
    def run(argv: list[str]) -> tuple[int, str]:
        return responses.get(tuple(argv), (127, ""))

    return run


def test_real_repo_pins_match_the_story():
    pins = doctor.load_pins(REAL_ROOT)
    assert pins.sdk_version == doctor.SemVer(10, 0, 402)
    assert pins.roll_forward == "latestFeature"
    assert pins.allow_prerelease is False
    assert pins.tools["python"] == "3.12.3"
    assert pins.tools["uv"] == "0.13.2"
    assert pins.tools["terraform"] == "1.16.6"
    assert pins.tools["buf"] == "1.74.0"
    assert "node" not in pins.tools
    assert pins.unity == doctor.UnitySpec("6000.3", "prefix", ".unity-version")


def test_install_section_is_the_local_development_heading():
    text = (REAL_ROOT / "docs/06-environments/local-development.md").read_text(encoding="utf-8")
    assert "## 1. Workstation prerequisites" in text
    assert doctor.INSTALL_DOC == INSTALL


def test_latest_feature_picks_highest_10_0_sdk_at_or_above_the_pin():
    requested = doctor.SemVer(10, 0, 402)
    installed = [
        doctor.SemVer(10, 0, 100),
        doctor.SemVer(10, 0, 402),
        doctor.SemVer(10, 0, 500),
        doctor.SemVer(10, 1, 0),
    ]
    assert doctor.select_sdk(installed, requested, "latestFeature") == doctor.SemVer(10, 0, 500)
    assert doctor.select_sdk([doctor.SemVer(10, 0, 100)], requested, "latestFeature") is None
    assert doctor.select_sdk(installed, requested, "disable") == requested


def test_patch_stays_in_feature_band_and_feature_uses_the_nearest_higher_band():
    requested = doctor.SemVer(10, 0, 402)
    installed = [doctor.SemVer(10, 0, 403), doctor.SemVer(10, 0, 500)]
    assert doctor.select_sdk(installed, requested, "patch") == doctor.SemVer(10, 0, 403)
    assert doctor.select_sdk([requested, doctor.SemVer(10, 0, 403)], requested, "patch") == requested
    assert doctor.select_sdk([doctor.SemVer(10, 0, 500)], requested, "feature") == doctor.SemVer(10, 0, 500)
    assert doctor.select_sdk(installed, requested, "feature") == doctor.SemVer(10, 0, 403)
    assert doctor.select_sdk(installed, requested, "latestPatch") == doctor.SemVer(10, 0, 403)


def test_happy_path_is_ok_and_checks_the_required_tools(tmp_path: Path):
    root = tmp_path / "repo"
    _write_pins(root)
    report = doctor.diagnose(root, runner=_runner(HAPPY), unity_versions=["6000.3.2f1", "6000.2.1f1"])
    assert report.ok
    assert [tool.name for tool in report.tools] == [
        "dotnet",
        "uv",
        "docker",
        "terraform",
        "git-lfs",
        "buf",
        "unity",
        "python",
    ]
    assert next(tool for tool in report.tools if tool.name == "dotnet").found == "10.0.500"
    assert next(tool for tool in report.tools if tool.name == "unity").found == "6000.3.2f1"
    table = doctor.to_table(report)
    assert "install: " + INSTALL in table
    payload = json.loads(doctor.to_json(report))
    assert payload["ok"] is True
    assert payload["install"] == INSTALL


def test_missing_tool_exits_nonzero_and_names_install_section(tmp_path: Path):
    root = tmp_path / "repo"
    _write_pins(root)
    responses = dict(HAPPY)
    del responses[("buf", "--version")]
    report = doctor.diagnose(root, runner=_runner(responses), unity_versions=["6000.3.0f1"])
    buf = next(tool for tool in report.tools if tool.name == "buf")
    assert report.ok is False
    assert buf.status == "missing"
    assert buf.found is None
    assert buf.install == INSTALL
    table = doctor.to_table(report)
    assert f"buf: missing; see {INSTALL}" in table
    payload = json.loads(doctor.to_json(report))
    assert payload["ok"] is False
    assert payload["tools"][5]["install"] == INSTALL


def test_version_mismatch_names_install_section(tmp_path: Path):
    root = tmp_path / "repo"
    _write_pins(root)
    responses = dict(HAPPY)
    responses[("terraform", "version")] = (0, "Terraform v1.10.0\n")
    report = doctor.diagnose(root, runner=_runner(responses), unity_versions=["6000.0.0f1"])
    terraform = next(tool for tool in report.tools if tool.name == "terraform")
    unity = next(tool for tool in report.tools if tool.name == "unity")
    assert terraform.status == "mismatch"
    assert terraform.found == "1.10.0"
    assert unity.status == "mismatch"
    assert INSTALL in doctor.to_table(report)
    assert json.loads(doctor.to_json(report))["tools"][3]["install"] == INSTALL


def test_python_accepts_a_newer_patch_in_the_same_minor(tmp_path: Path):
    root = tmp_path / "repo"
    _write_pins(root)
    responses = dict(HAPPY)
    responses[("python3", "--version")] = (127, "")
    responses[("python", "--version")] = (0, "Python 3.12.12\n")
    report = doctor.diagnose(root, runner=_runner(responses), unity_versions=["6000.3.1f1"])
    python = next(tool for tool in report.tools if tool.name == "python")
    assert python.status == "ok"
    assert python.found == "3.12.12"


def test_python_rejects_the_next_minor(tmp_path: Path):
    root = tmp_path / "repo"
    _write_pins(root)
    responses = dict(HAPPY)
    responses[("python3", "--version")] = (0, "Python 3.13.0\n")
    report = doctor.diagnose(root, runner=_runner(responses), unity_versions=["6000.3.1f1"])
    assert next(tool for tool in report.tools if tool.name == "python").status == "mismatch"


def test_project_version_txt_overrides_unity_prefix(tmp_path: Path):
    root = tmp_path / "repo"
    _write_pins(root)
    project = root / "client" / "ProjectSettings"
    project.mkdir(parents=True)
    (project / "ProjectVersion.txt").write_text("m_EditorVersion: 6000.3.8f1\n", encoding="utf-8")
    pins = doctor.load_pins(root)
    assert pins.unity.mode == "exact"
    assert pins.unity.value == "6000.3.8f1"
    report = doctor.diagnose(root, runner=_runner(HAPPY), unity_versions=["6000.3.2f1"])
    assert next(tool for tool in report.tools if tool.name == "unity").status == "mismatch"


def test_node_is_checked_only_when_pinned(tmp_path: Path):
    root = tmp_path / "repo"
    _write_pins(root, extra="node 22.14.0\n")
    responses = dict(HAPPY)
    responses[("node", "--version")] = (0, "v22.14.0\n")
    report = doctor.diagnose(root, runner=_runner(responses), unity_versions=["6000.3.0f1"])
    assert report.tools[-1].name == "node"
    assert report.tools[-1].status == "ok"


def test_disagreeing_terraform_pins_fail_and_name_the_install_section(tmp_path: Path):
    root = tmp_path / "repo"
    _write_pins(root, terraform_file="1.10.0")
    report = doctor.diagnose(root, runner=_runner({}), unity_versions=[])
    assert report.ok is False
    assert report.error is not None
    assert ".terraform-version" in report.error
    assert INSTALL in doctor.to_table(report)
    assert json.loads(doctor.to_json(report))["install"] == INSTALL


def test_unity_hub_folder_names_are_editor_versions(tmp_path: Path):
    hub = tmp_path / "Editor"
    (hub / "6000.3.2f1").mkdir(parents=True)
    (hub / "6000.2.0f1").mkdir()
    (hub / "not-an-editor").mkdir()
    found = doctor.installed_unity_versions(env={"UNITY_HUB_EDITORS": str(hub)}, platform="linux", home=tmp_path)
    assert found == ["6000.2.0f1", "6000.3.2f1"]


def test_cli_json_missing_tool_exits_nonzero(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    root = tmp_path / "repo"
    _write_pins(root)
    (root / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (root / "backlog").mkdir()
    monkeypatch.setenv("WR_REPO_ROOT", str(root))
    monkeypatch.setattr(doctor, "run_command", _runner({}))
    monkeypatch.setattr(doctor, "installed_unity_versions", lambda *args, **kwargs: [])
    code = cli.main(["doctor", "--json"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert code == 1
    assert payload["ok"] is False
    assert any(tool["status"] == "missing" and tool["install"] == INSTALL for tool in payload["tools"])
    assert captured.err == ""


def test_cli_table_ok_exits_zero(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    root = tmp_path / "repo"
    _write_pins(root)
    (root / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (root / "backlog").mkdir()
    monkeypatch.setenv("WR_REPO_ROOT", str(root))
    monkeypatch.setattr(doctor, "run_command", _runner(HAPPY))
    monkeypatch.setattr(doctor, "installed_unity_versions", lambda *args, **kwargs: ["6000.3.2f1"])
    code = cli.main(["doctor"])
    captured = capsys.readouterr()
    assert code == 0
    assert "dotnet" in captured.out
    assert "unity" in captured.out
    assert INSTALL in captured.out


def test_uv_on_path_reports_a_version():
    code, output = doctor.run_command(["uv", "--version"])
    assert code == 0
    assert doctor.parse_semver(output) is not None
