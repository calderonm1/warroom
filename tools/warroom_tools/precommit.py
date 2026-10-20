"""Pre-commit helpers for changed-file `dotnet format` and pinned gitleaks.

The git hook itself is `.pre-commit-config.yaml`. `make setup` installs it.
Ruff and `terraform fmt` run from upstream hook repos. These commands exist so
the C# and secret-scan hooks can stay inside the repo toolchain.
"""

from __future__ import annotations

import hashlib
import io
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import urllib.error
import urllib.request
import zipfile
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from .doctor import INSTALL_DOC

GITLEAKS_VERSION = "8.30.0"
GITLEAKS_BASE = f"https://github.com/gitleaks/gitleaks/releases/download/v{GITLEAKS_VERSION}"

# Official release checksums from gitleaks_8.30.0_checksums.txt.
_LINUX_X64 = "79a3ab579b53f71efd634f3aaf7e04a0fa0cf206b7ed434638d1547a2470a66e"
_LINUX_ARM64 = "b4cbbb6ddf7d1b2a603088cd03a4e3f7ce48ee7fd449b51f7de6ee2906f5fa2f"
_DARWIN_ARM64 = "b251ab2bcd4cd8ba9e56ff37698c033ebf38582b477d21ebd86586d927cf87e7"
_DARWIN_X64 = "ca221d012d247080c2f6f61f4b7a83bffa2453806b0c195c795bbe9a8c775ed5"
_WINDOWS_X64 = "54fe94f644b832dd08e8c3a5915efb3bfa862386d59fb27ca0792cb687a83573"


@dataclass(frozen=True)
class GitleaksAsset:
    filename: str
    sha256: str
    binary_name: str


GITLEAKS_ASSETS: dict[tuple[str, str], GitleaksAsset] = {
    ("linux", "x86_64"): GitleaksAsset(f"gitleaks_{GITLEAKS_VERSION}_linux_x64.tar.gz", _LINUX_X64, "gitleaks"),
    ("linux", "aarch64"): GitleaksAsset(f"gitleaks_{GITLEAKS_VERSION}_linux_arm64.tar.gz", _LINUX_ARM64, "gitleaks"),
    ("darwin", "x86_64"): GitleaksAsset(f"gitleaks_{GITLEAKS_VERSION}_darwin_x64.tar.gz", _DARWIN_X64, "gitleaks"),
    ("darwin", "aarch64"): GitleaksAsset(f"gitleaks_{GITLEAKS_VERSION}_darwin_arm64.tar.gz", _DARWIN_ARM64, "gitleaks"),
    ("windows", "x86_64"): GitleaksAsset(f"gitleaks_{GITLEAKS_VERSION}_windows_x64.zip", _WINDOWS_X64, "gitleaks.exe"),
}

Runner = Callable[[Sequence[str], Path], int]
Fetcher = Callable[[str], bytes]


class PrecommitError(RuntimeError):
    """A hook cannot run. The message is safe to print."""


def format_commands(root: Path, files: Sequence[str], *, dotnet: str = "dotnet") -> list[list[str]]:
    """One `dotnet format` invocation per solution or project, limited to changed C# files."""
    csharp = [_relative_file(root, raw) for raw in files if Path(raw).suffix == ".cs"]
    if not csharp:
        return []
    grouped: dict[Path, list[str]] = {}
    for relative in csharp:
        target = find_format_target(root, relative)
        if target is None:
            raise PrecommitError(
                f"dotnet format needs a .sln or .csproj for {relative}; none found at or above that file"
            )
        grouped.setdefault(target, []).append(relative)
    commands: list[list[str]] = []
    for target in sorted(grouped):
        included = grouped[target]
        commands.append(
            [
                dotnet,
                "format",
                _display(root, target),
                "--include=" + included[0],
                *included[1:],
                "--verbosity",
                "minimal",
            ]
        )
    return commands


def format_changed_csharp(
    root: Path,
    files: Sequence[str],
    *,
    dotnet: str | None,
    runner: Runner | None = None,
) -> int:
    """Format the given C# files. Returns a process exit code."""
    try:
        commands = format_commands(root, files, dotnet=dotnet or "dotnet")
    except PrecommitError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1
    if not commands:
        return 0
    if not dotnet:
        print(f"ERROR dotnet is required to format C#. See {INSTALL_DOC}", file=sys.stderr)
        return 1
    run = runner or _run
    for command in commands:
        command[0] = dotnet
        code = run(command, root)
        if code != 0:
            return code
    return 0


def find_format_target(root: Path, relative_file: str) -> Path | None:
    """Nearest `.sln`, otherwise nearest `.csproj`, walking from the file toward `root`."""
    root = root.resolve()
    directory = (root / relative_file).resolve().parent
    while True:
        try:
            directory.relative_to(root)
        except ValueError:
            return None
        solutions = sorted(path for path in directory.glob("*.sln") if path.is_file())
        if solutions:
            return solutions[0]
        projects = sorted(path for path in directory.glob("*.csproj") if path.is_file())
        if projects:
            return projects[0]
        if directory == root:
            return None
        directory = directory.parent


def gitleaks_argv(binary: Path) -> list[str]:
    """Staged-secret scan. Matches the upstream gitleaks pre-commit entry, with redaction."""
    return [str(binary), "git", "--pre-commit", "--redact", "--staged"]


def run_gitleaks(root: Path, *, binary: Path | None = None) -> int:
    try:
        resolved = binary or resolve_gitleaks_binary()
    except PrecommitError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1
    return _run(gitleaks_argv(resolved), root)


def resolve_gitleaks_binary() -> Path:
    """Use `gitleaks` on PATH when it exists. Otherwise install the pinned release."""
    found = shutil.which("gitleaks")
    if found:
        return Path(found)
    return install_pinned_gitleaks(gitleaks_cache_dir())


def gitleaks_cache_dir() -> Path:
    xdg = os.environ.get("XDG_CACHE_HOME")
    root = Path(xdg) if xdg else Path.home() / ".cache"
    return root / "warroom" / "gitleaks" / GITLEAKS_VERSION


def platform_key(system: str, machine: str) -> tuple[str, str]:
    system_name = {"linux": "linux", "darwin": "darwin", "windows": "windows"}.get(system.lower())
    machine_name = {"x86_64": "x86_64", "amd64": "x86_64", "aarch64": "aarch64", "arm64": "aarch64"}.get(
        machine.lower()
    )
    if system_name is None or machine_name is None:
        raise PrecommitError(
            f"gitleaks {GITLEAKS_VERSION} has no binary for {system} {machine}. Install gitleaks and put it on PATH."
        )
    return system_name, machine_name


def install_pinned_gitleaks(
    cache: Path,
    *,
    system: str | None = None,
    machine: str | None = None,
    fetch: Fetcher | None = None,
) -> Path:
    system_name = system if system is not None else platform.system()
    machine_name = machine if machine is not None else platform.machine()
    asset = GITLEAKS_ASSETS[platform_key(system_name, machine_name)]
    binary = cache / asset.binary_name
    if binary.is_file() and os.access(binary, os.X_OK):
        return binary
    url = f"{GITLEAKS_BASE}/{asset.filename}"
    data = (fetch or download)(url)
    verify_sha256(data, asset.sha256, asset.filename)
    return extract_archive(data, asset.filename, asset.binary_name, cache)


def verify_sha256(data: bytes, expected: str, label: str) -> None:
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        raise PrecommitError(f"gitleaks checksum mismatch for {label}: expected {expected} got {actual}")


def extract_archive(data: bytes, archive_name: str, binary_name: str, dest: Path) -> Path:
    """Write the top-level gitleaks binary from a release archive. Ignore every other member."""
    dest.mkdir(parents=True, exist_ok=True)
    payload = _read_member(data, archive_name, binary_name)
    target = dest / binary_name
    target.write_bytes(payload)
    target.chmod(0o755)
    return target


def download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "warroom-tools"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.read()
    except urllib.error.URLError as exc:
        raise PrecommitError(f"could not download gitleaks from {url}: {exc}") from exc


def _read_member(data: bytes, archive_name: str, binary_name: str) -> bytes:
    if archive_name.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            name = _exact_member([info.filename for info in archive.infolist() if not info.is_dir()], binary_name)
            return archive.read(name)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        names = [member.name for member in archive.getmembers() if member.isfile()]
        name = _exact_member(names, binary_name)
        extracted = archive.extractfile(name)
        if extracted is None:
            raise PrecommitError(f"archive {archive_name} does not contain {binary_name}")
        return extracted.read()


def _exact_member(names: Sequence[str], binary_name: str) -> str:
    for name in names:
        if name == binary_name or name == f"./{binary_name}":
            return name
    raise PrecommitError(f"archive does not contain a top-level {binary_name}")


def _relative_file(root: Path, raw: str) -> str:
    path = Path(raw)
    if path.is_absolute():
        try:
            relative = path.resolve().relative_to(root.resolve())
        except ValueError as exc:
            raise PrecommitError(f"refusing path outside the repo: {raw}") from exc
    else:
        if ".." in path.parts:
            raise PrecommitError(f"refusing path outside the repo: {raw}")
        relative = path
    return relative.as_posix()


def _display(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _run(command: Sequence[str], cwd: Path) -> int:
    completed = subprocess.run(list(command), cwd=cwd, check=False)
    return completed.returncode
