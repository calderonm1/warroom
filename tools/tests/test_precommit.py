"""ST-02.1.2: pre-commit runs ruff, dotnet format, terraform fmt and gitleaks."""

from __future__ import annotations

import hashlib
import io
import tarfile
import zipfile
from pathlib import Path

import pytest
import yaml
from conftest import REAL_ROOT

from warroom_tools import precommit
from warroom_tools.doctor import INSTALL_DOC

CONFIG = REAL_ROOT / ".pre-commit-config.yaml"


def _hooks() -> list[dict]:
    data = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    hooks = []
    for repo in data["repos"]:
        for hook in repo["hooks"]:
            hook = dict(hook)
            hook["repo"] = repo["repo"]
            hook["rev"] = repo.get("rev")
            hooks.append(hook)
    return hooks


def _hook(hook_id: str) -> dict:
    matches = [hook for hook in _hooks() if hook["id"] == hook_id]
    assert len(matches) == 1
    return matches[0]


def test_config_runs_ruff_dotnet_format_terraform_fmt_and_gitleaks():
    ids = {hook["id"] for hook in _hooks()}
    assert {"ruff-check", "ruff-format", "dotnet-format", "terraform_fmt", "gitleaks"} <= ids

    ruff = _hook("ruff-check")
    assert ruff["repo"] == "https://github.com/astral-sh/ruff-pre-commit"
    assert ruff["args"] == ["--fix"]
    assert _hook("ruff-format")["repo"] == ruff["repo"]

    dotnet = _hook("dotnet-format")
    assert dotnet["name"] == "dotnet format (changed files)"
    assert dotnet["entry"] == "uv run --frozen wr precommit dotnet-format"
    assert dotnet["pass_filenames"] is True

    terraform = _hook("terraform_fmt")
    assert terraform["repo"] == "https://github.com/antonbabenko/pre-commit-terraform"
    assert "--hook-config=--tf-path=terraform" in terraform["args"]

    gitleaks = _hook("gitleaks")
    assert gitleaks["entry"] == "uv run --frozen wr precommit gitleaks"
    assert gitleaks["pass_filenames"] is False


def test_ruff_hook_matches_the_locked_ruff_version():
    text = (REAL_ROOT / "uv.lock").read_text(encoding="utf-8")
    marker = '[[package]]\nname = "ruff"\nversion = "'
    start = text.index(marker) + len(marker)
    locked = text[start : text.index('"', start)]
    assert _hook("ruff-check")["rev"] == f"v{locked}"


def test_terraform_fmt_pins_the_repo_terraform_version():
    pinned = (REAL_ROOT / ".terraform-version").read_text(encoding="utf-8").strip()
    assert f"--hook-config=--tool-version={pinned}" in _hook("terraform_fmt")["args"]
    assert "--hook-config=--tool-version-mode=prefer-local" in _hook("terraform_fmt")["args"]


def test_make_setup_installs_precommit_hooks():
    text = (REAL_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "pre-commit install" in text
    assert "uv sync --frozen" in text


def test_local_development_documents_the_hooks():
    text = (REAL_ROOT / "docs/06-environments/local-development.md").read_text(encoding="utf-8")
    assert ".pre-commit-config.yaml" in text
    assert "ruff" in text
    assert "dotnet format" in text
    assert "terraform fmt" in text
    assert "gitleaks" in text
    assert "make setup" in text
    assert "pre-commit install" in text


def test_format_commands_include_only_changed_csharp_files(tmp_path: Path):
    (tmp_path / "server").mkdir()
    (tmp_path / "server" / "WarRoom.sln").write_text("", encoding="utf-8")
    (tmp_path / "server" / "App").mkdir()
    (tmp_path / "server" / "App" / "App.csproj").write_text("", encoding="utf-8")
    (tmp_path / "server" / "App" / "Program.cs").write_text("", encoding="utf-8")
    (tmp_path / "notes.md").write_text("", encoding="utf-8")

    commands = precommit.format_commands(
        tmp_path,
        ["server/App/Program.cs", "notes.md", "server/App/Other.cs"],
    )
    assert commands == [
        [
            "dotnet",
            "format",
            "server/App/App.csproj",
            "--include=server/App/Program.cs",
            "server/App/Other.cs",
            "--verbosity",
            "minimal",
        ]
    ]


def test_format_commands_group_files_by_nearest_project(tmp_path: Path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    (tmp_path / "a" / "A.csproj").write_text("", encoding="utf-8")
    (tmp_path / "b" / "B.csproj").write_text("", encoding="utf-8")

    commands = precommit.format_commands(tmp_path, ["b/B.cs", "a/A.cs"])
    assert [command[2] for command in commands] == ["a/A.csproj", "b/B.csproj"]
    assert commands[0][3] == "--include=a/A.cs"
    assert commands[1][3] == "--include=b/B.cs"


def test_format_commands_prefer_a_solution_in_the_same_directory(tmp_path: Path):
    (tmp_path / "App.sln").write_text("", encoding="utf-8")
    (tmp_path / "App.csproj").write_text("", encoding="utf-8")
    commands = precommit.format_commands(tmp_path, ["Program.cs"])
    assert commands[0][2] == "App.sln"


def test_format_changed_csharp_skips_when_there_are_no_csharp_files(tmp_path: Path):
    calls: list[list[str]] = []

    def runner(command, cwd):
        calls.append(list(command))
        return 0

    code = precommit.format_changed_csharp(tmp_path, ["README.md"], dotnet=None, runner=runner)
    assert code == 0
    assert calls == []


def test_format_changed_csharp_names_the_install_doc_when_dotnet_is_missing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    (tmp_path / "App.csproj").write_text("", encoding="utf-8")
    code = precommit.format_changed_csharp(tmp_path, ["Program.cs"], dotnet=None)
    assert code == 1
    assert INSTALL_DOC in capsys.readouterr().err


def test_format_changed_csharp_fails_when_no_project_contains_the_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    code = precommit.format_changed_csharp(tmp_path, ["Orphan.cs"], dotnet="dotnet")
    assert code == 1
    assert "Orphan.cs" in capsys.readouterr().err


def test_format_changed_csharp_invokes_the_dotnet_binary(tmp_path: Path):
    (tmp_path / "App.csproj").write_text("", encoding="utf-8")
    seen: list[tuple[list[str], Path]] = []

    def runner(command, cwd):
        seen.append((list(command), cwd))
        return 0

    code = precommit.format_changed_csharp(tmp_path, ["Program.cs"], dotnet="/usr/bin/dotnet", runner=runner)
    assert code == 0
    assert seen[0][0][0] == "/usr/bin/dotnet"
    assert seen[0][0][1:4] == ["format", "App.csproj", "--include=Program.cs"]
    assert seen[0][1] == tmp_path


def test_format_changed_csharp_refuses_paths_outside_the_repo(tmp_path: Path):
    with pytest.raises(precommit.PrecommitError):
        precommit.format_commands(tmp_path, ["../Secret.cs"])


def test_gitleaks_argv_scans_staged_changes_without_filenames():
    argv = precommit.gitleaks_argv(Path("/opt/gitleaks"))
    assert argv == ["/opt/gitleaks", "git", "--pre-commit", "--redact", "--staged"]


def test_resolve_gitleaks_binary_prefers_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    binary = tmp_path / "gitleaks"
    binary.write_text("#!/bin/sh\n", encoding="utf-8")
    binary.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path))
    assert precommit.resolve_gitleaks_binary() == binary


def test_install_pinned_gitleaks_checks_the_checksum_and_extracts_the_binary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    payload = b"#!/bin/sh\necho gitleaks\n"
    archive = _tar_bytes({"gitleaks": payload, "../evil": b"x", "nested/gitleaks": b"nope"})
    asset = precommit.GITLEAKS_ASSETS[("linux", "x86_64")]
    patched = precommit.GitleaksAsset(asset.filename, hashlib.sha256(archive).hexdigest(), asset.binary_name)
    monkeypatch.setitem(precommit.GITLEAKS_ASSETS, ("linux", "x86_64"), patched)

    def fetch(url: str) -> bytes:
        assert url.endswith(asset.filename)
        return archive

    binary = precommit.install_pinned_gitleaks(tmp_path, system="linux", machine="x86_64", fetch=fetch)
    assert binary.read_bytes() == payload
    assert not (tmp_path.parent / "evil").exists()
    assert binary.stat().st_mode & 0o111


def test_verify_sha256_rejects_a_mismatch():
    with pytest.raises(precommit.PrecommitError, match="checksum mismatch"):
        precommit.verify_sha256(b"not-the-release", "ab" * 32, "gitleaks.tar.gz")


def test_extract_archive_reads_a_windows_zip(tmp_path: Path):
    payload = b"MZ-gitleaks"
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("gitleaks.exe", payload)
        archive.writestr("../evil.exe", b"x")
    binary = precommit.extract_archive(buffer.getvalue(), "gitleaks_windows_x64.zip", "gitleaks.exe", tmp_path)
    assert binary.read_bytes() == payload
    assert not (tmp_path.parent / "evil.exe").exists()


def test_platform_key_rejects_unknown_machines():
    with pytest.raises(precommit.PrecommitError, match="no binary"):
        precommit.platform_key("linux", "riscv64")


def _tar_bytes(members: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        for name, payload in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(payload)
            archive.addfile(info, io.BytesIO(payload))
    return buffer.getvalue()
