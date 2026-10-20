"""Workstation toolchain check (`wr doctor` / `make doctor`).

Pins live in `global.json`, `.tool-versions`, `.terraform-version` and `.unity-version`.
A missing or wrong tool exits non-zero and names the install section in
`docs/06-environments/local-development.md`.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

INSTALL_DOC = "docs/06-environments/local-development.md#1-workstation-prerequisites"

# .NET SDK feature bands are the hundreds group of the three-digit patch (10.0.402 -> 4).
ROLL_FORWARDS = frozenset(
    {
        "disable",
        "patch",
        "feature",
        "minor",
        "major",
        "latestPatch",
        "latestFeature",
        "latestMinor",
        "latestMajor",
    }
)
REQUIRED_TOOL_VERSIONS = ("python", "uv", "terraform", "buf")
UNITY_VERSION_RE = re.compile(r"\d+\.\d+\.\d+[abf]\d+")
_SEMVER_RE = re.compile(r"(\d+)\.(\d+)\.(\d+)")
_EDITOR_LINE_RE = re.compile(r"^m_EditorVersion:\s*(\S+)\s*$", re.MULTILINE)

Status = Literal["ok", "missing", "mismatch"]
Runner = Callable[[Sequence[str]], tuple[int, str]]


class PinError(Exception):
    """A toolchain pin file is missing or not in the expected shape."""


@dataclass(frozen=True, order=True)
class SemVer:
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


@dataclass(frozen=True)
class UnitySpec:
    value: str
    mode: Literal["exact", "prefix"]
    source: str

    @property
    def expected(self) -> str:
        return self.value if self.mode == "exact" else f"{self.value}.x"


@dataclass(frozen=True)
class Pins:
    sdk_version: SemVer
    roll_forward: str
    allow_prerelease: bool
    tools: dict[str, str]
    unity: UnitySpec


@dataclass(frozen=True)
class ToolCheck:
    name: str
    status: Status
    expected: str
    found: str | None
    install: str


@dataclass(frozen=True)
class DoctorReport:
    tools: tuple[ToolCheck, ...]
    install: str
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and all(tool.status == "ok" for tool in self.tools)


def parse_semver(text: str) -> SemVer | None:
    match = _SEMVER_RE.search(text)
    if not match:
        return None
    return SemVer(int(match.group(1)), int(match.group(2)), int(match.group(3)))


def feature_band(version: SemVer) -> int:
    return version.patch // 100


def select_sdk(installed: Sequence[SemVer], requested: SemVer, roll_forward: str) -> SemVer | None:
    """Pick the SDK `global.json` rollForward would use. Never rolls backward."""

    def at_least(version: SemVer) -> bool:
        return version >= requested

    def in_band(version: SemVer) -> bool:
        return (
            version.major == requested.major
            and version.minor == requested.minor
            and feature_band(version) == feature_band(requested)
            and at_least(version)
        )

    if roll_forward not in ROLL_FORWARDS:
        raise PinError(f"unsupported rollForward '{roll_forward}'")

    if roll_forward == "disable":
        return requested if requested in installed else None

    if roll_forward in {"patch", "latestPatch"}:
        pool = [version for version in installed if in_band(version)]
        if roll_forward == "patch" and requested in installed:
            return requested
        return max(pool) if pool else None

    if roll_forward == "feature":
        if requested in installed:
            return requested
        same_band = [version for version in installed if in_band(version)]
        if same_band:
            return max(same_band)
        higher = [
            version
            for version in installed
            if version.major == requested.major
            and version.minor == requested.minor
            and feature_band(version) > feature_band(requested)
        ]
        if not higher:
            return None
        nearest = min(feature_band(version) for version in higher)
        return max(version for version in higher if feature_band(version) == nearest)

    if roll_forward == "latestFeature":
        pool = [
            version
            for version in installed
            if version.major == requested.major and version.minor == requested.minor and at_least(version)
        ]
        return max(pool) if pool else None

    if roll_forward in {"minor", "latestMinor"}:
        pool = [version for version in installed if version.major == requested.major and at_least(version)]
        if roll_forward == "minor" and requested in installed:
            return requested
        return max(pool) if pool else None

    pool = [version for version in installed if at_least(version)]
    if roll_forward == "major" and requested in installed:
        return requested
    return max(pool) if pool else None


def run_command(argv: Sequence[str]) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            list(argv),
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (FileNotFoundError, OSError):
        return 127, ""
    except subprocess.TimeoutExpired:
        return 124, ""
    return completed.returncode, f"{completed.stdout or ''}{completed.stderr or ''}"


def installed_unity_versions(
    env: Mapping[str, str] | None = None,
    platform: str | None = None,
    home: Path | None = None,
) -> list[str]:
    """Editor versions installed under Unity Hub (folder name is the version)."""
    env = os.environ if env is None else env
    platform = sys.platform if platform is None else platform
    home = Path.home() if home is None else home
    custom = env.get("UNITY_HUB_EDITORS", "")
    if custom:
        roots = [Path(entry) for entry in custom.split(os.pathsep) if entry]
    else:
        roots = list(_default_hub_roots(platform, home, env))
    found: list[str] = []
    for root in roots:
        if not root.is_dir():
            continue
        for child in sorted(root.iterdir()):
            if child.is_dir() and UNITY_VERSION_RE.fullmatch(child.name):
                found.append(child.name)
    return found


def load_pins(root: Path) -> Pins:
    sdk_version, roll_forward, allow_prerelease = _load_global_json(root / "global.json")
    tools = _load_tool_versions(root / ".tool-versions")
    missing = [name for name in REQUIRED_TOOL_VERSIONS if name not in tools]
    if missing:
        raise PinError(f".tool-versions is missing {', '.join(missing)}")
    for name in (*REQUIRED_TOOL_VERSIONS, "node"):
        if name in tools and parse_semver(tools[name]) is None:
            raise PinError(f".tool-versions {name} version '{tools[name]}' is not major.minor.patch")
    terraform = _load_single_version(root / ".terraform-version")
    if terraform != tools["terraform"]:
        raise PinError(f".terraform-version ({terraform}) and .tool-versions terraform ({tools['terraform']}) disagree")
    return Pins(
        sdk_version=sdk_version,
        roll_forward=roll_forward,
        allow_prerelease=allow_prerelease,
        tools=tools,
        unity=_load_unity_spec(root),
    )


def diagnose(
    root: Path,
    runner: Runner | None = None,
    unity_versions: list[str] | None = None,
) -> DoctorReport:
    try:
        pins = load_pins(root)
    except PinError as exc:
        return DoctorReport(tools=(), install=INSTALL_DOC, error=str(exc))
    except (OSError, json.JSONDecodeError) as exc:
        return DoctorReport(tools=(), install=INSTALL_DOC, error=f"unreadable toolchain pin: {exc}")

    run = runner or run_command
    editors = installed_unity_versions() if unity_versions is None else unity_versions
    checks = [
        _check_dotnet(pins, run),
        _check_uv(pins, run),
        _check_presence("docker", ["docker", "--version"], run),
        _check_exact("terraform", pins.tools["terraform"], ["terraform", "version"], run),
        _check_presence("git-lfs", ["git", "lfs", "version"], run),
        _check_exact("buf", pins.tools["buf"], ["buf", "--version"], run),
        _check_unity(pins.unity, editors),
        _check_python(pins, run),
    ]
    if "node" in pins.tools:
        checks.append(_check_exact("node", pins.tools["node"], ["node", "--version"], run))
    return DoctorReport(tools=tuple(checks), install=INSTALL_DOC)


def to_json(report: DoctorReport) -> str:
    payload: dict[str, object] = {
        "ok": report.ok,
        "install": report.install,
        "tools": [
            {
                "name": tool.name,
                "status": tool.status,
                "expected": tool.expected,
                "found": tool.found,
                "install": tool.install,
            }
            for tool in report.tools
        ],
    }
    if report.error:
        payload["error"] = report.error
    return json.dumps(payload, indent=2)


def to_table(report: DoctorReport) -> str:
    rows = [(tool.name, tool.status, tool.expected, tool.found or "-") for tool in report.tools]
    header = ("TOOL", "STATUS", "EXPECTED", "FOUND")
    widths = [len(column) for column in header]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))

    def render(cells: tuple[str, ...]) -> str:
        return "  ".join(cell.ljust(widths[index]) for index, cell in enumerate(cells)).rstrip()

    lines = [render(header), render(tuple("-" * width for width in widths))]
    lines.extend(render(row) for row in rows)
    if report.error:
        lines.append(f"ERROR pins: {report.error}; see {report.install}")
    for tool in report.tools:
        if tool.status != "ok":
            lines.append(f"{tool.name}: {tool.status}; see {tool.install}")
    if report.ok:
        lines.append(f"install: {report.install}")
    return "\n".join(lines)


def _check_dotnet(pins: Pins, runner: Runner) -> ToolCheck:
    expected = f"{pins.sdk_version} ({pins.sdk_version.major}.{pins.sdk_version.minor}.x, {pins.roll_forward})"
    code, output = runner(["dotnet", "--list-sdks"])
    if code != 0:
        return _result("dotnet", "missing", expected, None)
    installed = _parse_sdk_list(output, pins.allow_prerelease)
    if not installed:
        return _result("dotnet", "missing", expected, None)
    chosen = select_sdk(installed, pins.sdk_version, pins.roll_forward)
    if chosen is None:
        found = ", ".join(str(version) for version in sorted(set(installed)))
        return _result("dotnet", "mismatch", expected, found)
    return _result("dotnet", "ok", expected, str(chosen))


def _check_python(pins: Pins, runner: Runner) -> ToolCheck:
    pin = parse_semver(pins.tools["python"])
    assert pin is not None
    expected = f">={pin},<{pin.major}.{pin.minor + 1}"
    code, output = _first_present(runner, (["python3", "--version"], ["python", "--version"]))
    if code != 0:
        return _result("python", "missing", expected, None)
    found = parse_semver(output)
    if found is None:
        return _result("python", "mismatch", expected, None)
    if found.major == pin.major and found.minor == pin.minor and found >= pin:
        return _result("python", "ok", expected, str(found))
    return _result("python", "mismatch", expected, str(found))


def _check_uv(pins: Pins, runner: Runner) -> ToolCheck:
    return _check_exact("uv", pins.tools["uv"], ["uv", "--version"], runner)


def _check_unity(spec: UnitySpec, versions: Sequence[str]) -> ToolCheck:
    matches = [version for version in versions if _unity_matches(version, spec)]
    if matches:
        return _result("unity", "ok", spec.expected, matches[0])
    if not versions:
        return _result("unity", "missing", spec.expected, None)
    return _result("unity", "mismatch", spec.expected, ", ".join(versions))


def _check_exact(name: str, expected: str, argv: Sequence[str], runner: Runner) -> ToolCheck:
    code, output = runner(argv)
    if code != 0:
        return _result(name, "missing", expected, None)
    found = parse_semver(output)
    if found is None:
        return _result(name, "mismatch", expected, None)
    status: Status = "ok" if str(found) == expected else "mismatch"
    return _result(name, status, expected, str(found))


def _check_presence(name: str, argv: Sequence[str], runner: Runner) -> ToolCheck:
    code, output = runner(argv)
    if code != 0:
        return _result(name, "missing", "any", None)
    found = parse_semver(output)
    if found is None:
        return _result(name, "mismatch", "any", None)
    return _result(name, "ok", "any", str(found))


def _result(name: str, status: Status, expected: str, found: str | None) -> ToolCheck:
    return ToolCheck(name=name, status=status, expected=expected, found=found, install=INSTALL_DOC)


def _unity_matches(version: str, spec: UnitySpec) -> bool:
    if spec.mode == "exact":
        return version == spec.value
    return version.startswith(f"{spec.value}.")


def _first_present(runner: Runner, commands: Sequence[Sequence[str]]) -> tuple[int, str]:
    last = (127, "")
    for argv in commands:
        code, output = runner(argv)
        if code != 127:
            return code, output
        last = (code, output)
    return last


def _parse_sdk_list(text: str, allow_prerelease: bool) -> list[SemVer]:
    found: list[SemVer] = []
    for line in text.splitlines():
        token = line.split(" ", 1)[0] if line.strip() else ""
        if not token or ("-" in token and not allow_prerelease):
            continue
        parsed = parse_semver(token)
        if parsed is not None:
            found.append(parsed)
    return found


def _load_global_json(path: Path) -> tuple[SemVer, str, bool]:
    if not path.is_file():
        raise PinError("missing global.json")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PinError(f"global.json is not JSON: {exc}") from exc
    sdk = data.get("sdk") if isinstance(data, dict) else None
    if not isinstance(sdk, dict):
        raise PinError("global.json needs an sdk object")
    version = parse_semver(str(sdk.get("version", "")))
    if version is None:
        raise PinError("global.json sdk.version must be major.minor.patch")
    roll_forward = str(sdk.get("rollForward", ""))
    if roll_forward not in ROLL_FORWARDS:
        raise PinError(f"global.json sdk.rollForward '{roll_forward}' is not a supported policy")
    allow = sdk.get("allowPrerelease", False)
    if not isinstance(allow, bool):
        raise PinError("global.json sdk.allowPrerelease must be a boolean")
    return version, roll_forward, allow


def _load_tool_versions(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise PinError("missing .tool-versions")
    tools: dict[str, str] = {}
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 2:
            raise PinError(f".tool-versions:{lineno} must be 'name version'")
        name, version = parts
        if name in tools:
            raise PinError(f".tool-versions:{lineno} duplicates {name}")
        tools[name] = version
    return tools


def _load_single_version(path: Path) -> str:
    if not path.is_file():
        raise PinError(f"missing {path.name}")
    lines = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            lines.append(line)
    if len(lines) != 1 or parse_semver(lines[0]) is None:
        raise PinError(f"{path.name} must contain one major.minor.patch version")
    return str(parse_semver(lines[0]))


def _load_unity_spec(root: Path) -> UnitySpec:
    project = root / "client" / "ProjectSettings" / "ProjectVersion.txt"
    if project.is_file():
        match = _EDITOR_LINE_RE.search(project.read_text(encoding="utf-8"))
        if match is None or UNITY_VERSION_RE.fullmatch(match.group(1)) is None:
            raise PinError("client/ProjectSettings/ProjectVersion.txt has no m_EditorVersion")
        return UnitySpec(match.group(1), "exact", project.as_posix())
    pin = root / ".unity-version"
    if not pin.is_file():
        raise PinError("missing .unity-version (or client/ProjectSettings/ProjectVersion.txt)")
    text = pin.read_text(encoding="utf-8").strip().split("#", 1)[0].strip()
    if UNITY_VERSION_RE.fullmatch(text):
        return UnitySpec(text, "exact", ".unity-version")
    if re.fullmatch(r"\d+\.\d+", text):
        return UnitySpec(text, "prefix", ".unity-version")
    raise PinError(".unity-version must be '6000.3' or a full editor version such as 6000.3.0f1")


def _default_hub_roots(platform: str, home: Path, env: Mapping[str, str]) -> tuple[Path, ...]:
    if platform == "darwin":
        return (Path("/Applications/Unity/Hub/Editor"), home / "Applications/Unity/Hub/Editor")
    if platform == "win32":
        program = Path(env.get("PROGRAMFILES", "C:/Program Files"))
        return (program / "Unity/Hub/Editor",)
    return (home / "Unity/Hub/Editor", Path("/opt/unity/editors"))
