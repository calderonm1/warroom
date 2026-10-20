"""Create the reference Android emulator profiles (`wr android-avd` / `make android-avd`).

Profiles are the ones named in `docs/06-environments/device-testing.md` (ST-02.5.1).
API 29 follows that doc's proposed floor. OQ-009 stays open.
"""

from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

INSTALL_DOC = "docs/06-environments/device-testing.md#4-android-emulator-profiles"

_AVD_NAME_RE = re.compile(r"^\s*Name:\s*(\S+)\s*$", re.MULTILINE)
_DEVICE_QUOTED_RE = re.compile(r'id:\s*(?:\d+\s+or\s+)?"([^"]+)"', re.IGNORECASE)
_DEVICE_BARE_RE = re.compile(r"^\s*id:\s*([A-Za-z_][A-Za-z0-9_]*)\s*$", re.MULTILINE)
_AVAILABLE_RE = re.compile(r"^Available Packages\b", re.IGNORECASE)

Action = Literal["exists", "created"]
Runner = Callable[[Sequence[str], str | None, float], "CmdResult"]


@dataclass(frozen=True)
class Profile:
    name: str
    api: int
    device: str
    ram_mb: int | None = None
    gpu_mode: str | None = None

    def package(self, abi: str) -> str:
        return f"system-images;android-{self.api};google_apis;{abi}"

    def hardware_updates(self) -> tuple[tuple[str, str], ...]:
        updates: list[tuple[str, str]] = []
        if self.ram_mb is not None:
            updates.append(("hw.ramSize", str(self.ram_mb)))
        if self.gpu_mode is not None:
            updates.append(("hw.gpu.enabled", "yes"))
            updates.append(("hw.gpu.mode", self.gpu_mode))
        return tuple(updates)


# Order is the create order and the order of command output.
PROFILES: tuple[Profile, ...] = (
    Profile(name="wr_pixel_api35", api=35, device="pixel_8", ram_mb=4096, gpu_mode="host"),
    Profile(name="wr_small_api29", api=29, device="small_phone"),
)


@dataclass(frozen=True)
class CmdResult:
    code: int
    out: str
    err: str

    @property
    def text(self) -> str:
        return f"{self.out}{self.err}"


@dataclass(frozen=True)
class Outcome:
    name: str
    action: Action
    device: str
    api: int
    abi: str
    package: str
    ram_mb: int | None


@dataclass(frozen=True)
class Report:
    outcomes: tuple[Outcome, ...]
    abi: str
    error: str | None = None
    install: str = INSTALL_DOC

    @property
    def ok(self) -> bool:
        return self.error is None and {item.name for item in self.outcomes} == {profile.name for profile in PROFILES}


def abi_for_machine(machine: str) -> str:
    """arm64 hosts boot arm64-v8a images. x86_64 hosts boot x86_64 images."""

    normalized = machine.lower().replace("-", "_")
    if normalized in {"arm64", "aarch64", "arm64e"}:
        return "arm64-v8a"
    return "x86_64"


def parse_avd_names(text: str) -> set[str]:
    return set(_AVD_NAME_RE.findall(text))


def parse_device_ids(text: str) -> set[str]:
    found = set(_DEVICE_QUOTED_RE.findall(text))
    found.update(_DEVICE_BARE_RE.findall(text))
    return found


def parse_installed_packages(text: str) -> set[str]:
    lines = text.splitlines()
    end = len(lines)
    for index, line in enumerate(lines):
        if _AVAILABLE_RE.match(line.strip()):
            end = index
            break
    packages: set[str] = set()
    for line in lines[:end]:
        token = line.strip().split("|", 1)[0].strip()
        if token.startswith("system-images;"):
            packages.add(token)
    return packages


def apply_hardware(text: str, profile: Profile) -> str:
    updates = dict(profile.hardware_updates())
    if not updates:
        return text
    seen: set[str] = set()
    rewritten: list[str] = []
    for line in text.splitlines():
        key, separator, _value = line.partition("=")
        stripped = key.strip()
        if separator and stripped in updates:
            rewritten.append(f"{stripped}={updates[stripped]}")
            seen.add(stripped)
        else:
            rewritten.append(line)
    for key, value in profile.hardware_updates():
        if key not in seen:
            rewritten.append(f"{key}={value}")
    body = "\n".join(rewritten)
    return f"{body}\n" if body else ""


def run_command(argv: Sequence[str], stdin: str | None = None, timeout: float = 60) -> CmdResult:
    try:
        completed = subprocess.run(
            list(argv),
            input=stdin,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (FileNotFoundError, OSError) as exc:
        return CmdResult(127, "", str(exc))
    except subprocess.TimeoutExpired:
        return CmdResult(124, "", f"timed out after {timeout:.0f}s")
    return CmdResult(completed.returncode, completed.stdout or "", completed.stderr or "")


def sdk_roots(env: Mapping[str, str], platform_name: str, home: Path) -> tuple[Path, ...]:
    roots: list[Path] = []
    for key in ("ANDROID_HOME", "ANDROID_SDK_ROOT"):
        value = env.get(key, "").strip()
        if value:
            roots.append(Path(value))
    if platform_name == "darwin":
        roots.append(home / "Library/Android/sdk")
    elif platform_name == "win32":
        local = env.get("LOCALAPPDATA", "")
        if local:
            roots.append(Path(local) / "Android/Sdk")
    else:
        roots.append(home / "Android/Sdk")
    return tuple(roots)


def _tool_names(name: str, platform_name: str) -> tuple[str, ...]:
    if platform_name == "win32":
        return (f"{name}.bat", f"{name}.cmd", name)
    return (name,)


def locate_tool(name: str, env: Mapping[str, str], platform_name: str, home: Path) -> Path | None:
    for candidate_name in _tool_names(name, platform_name):
        found = shutil.which(candidate_name, path=env.get("PATH"))
        if found:
            return Path(found)
    for root in sdk_roots(env, platform_name, home):
        bases = [
            root / "cmdline-tools" / "latest" / "bin",
            root / "tools" / "bin",
        ]
        cmdline = root / "cmdline-tools"
        if cmdline.is_dir():
            bases.extend(sorted(path / "bin" for path in cmdline.iterdir() if path.is_dir() and path.name != "latest"))
        for base in bases:
            for candidate_name in _tool_names(name, platform_name):
                candidate = base / candidate_name
                if candidate.is_file():
                    return candidate
    return None


def avd_home_dir(env: Mapping[str, str], home: Path) -> Path:
    custom = env.get("ANDROID_AVD_HOME", "").strip()
    if custom:
        return Path(custom)
    return home / ".android" / "avd"


def _fail(message: str, outcomes: list[Outcome], abi: str) -> Report:
    return Report(outcomes=tuple(outcomes), abi=abi, error=f"{message} See {INSTALL_DOC}.")


def _run(runner: Runner, argv: Sequence[str], stdin: str | None, timeout: float) -> CmdResult:
    return runner(list(argv), stdin, timeout)


def ensure(
    *,
    sdkmanager: Path | None,
    avdmanager: Path | None,
    runner: Runner,
    machine: str,
    avd_home: Path,
) -> Report:
    abi = abi_for_machine(machine)
    if sdkmanager is None or avdmanager is None:
        missing = [name for name, path in (("sdkmanager", sdkmanager), ("avdmanager", avdmanager)) if path is None]
        joined = " and ".join(missing)
        return _fail(
            f"{joined} not found. Install Android Studio or the command-line tools and set ANDROID_HOME.",
            [],
            abi,
        )

    listed = _run(runner, [str(avdmanager), "list", "avd"], None, 60)
    if listed.code != 0:
        return _fail(f"avdmanager list avd failed ({listed.code}): {listed.text.strip()}", [], abi)
    existing = parse_avd_names(listed.text)
    done: dict[str, Outcome] = {}
    for profile in PROFILES:
        if profile.name in existing:
            done[profile.name] = _outcome(profile, "exists", abi)
    missing_profiles = [profile for profile in PROFILES if profile.name not in done]

    def partial() -> list[Outcome]:
        return [done[profile.name] for profile in PROFILES if profile.name in done]

    if not missing_profiles:
        return Report(outcomes=tuple(partial()), abi=abi)

    devices = _run(runner, [str(avdmanager), "list", "device"], None, 60)
    if devices.code != 0:
        return _fail(f"avdmanager list device failed ({devices.code}): {devices.text.strip()}", partial(), abi)
    device_ids = parse_device_ids(devices.text)
    for profile in missing_profiles:
        if profile.device not in device_ids:
            return _fail(
                f"device profile {profile.device!r} is not in this SDK (needed for {profile.name}). "
                "Update the Android SDK command-line tools.",
                partial(),
                abi,
            )

    installed_cmd = _run(runner, [str(sdkmanager), "--list_installed"], None, 120)
    if installed_cmd.code == 0:
        installed = parse_installed_packages(installed_cmd.text)
    else:
        fallback = _run(runner, [str(sdkmanager), "--list"], None, 180)
        if fallback.code != 0:
            return _fail(
                f"sdkmanager --list_installed failed ({installed_cmd.code}): {installed_cmd.text.strip()}",
                partial(),
                abi,
            )
        installed = parse_installed_packages(fallback.text)

    needs_package = [profile for profile in missing_profiles if profile.package(abi) not in installed]
    if needs_package:
        licences = _run(runner, [str(sdkmanager), "--licenses"], "y\n" * 80, 180)
        if licences.code != 0:
            return _fail(
                f"sdkmanager --licenses failed ({licences.code}): {licences.text.strip()}",
                partial(),
                abi,
            )
        for profile in needs_package:
            package = profile.package(abi)
            installed_pkg = _run(runner, [str(sdkmanager), "--install", package], None, 1800)
            if installed_pkg.code != 0:
                return _fail(
                    f"sdkmanager --install {package} failed ({installed_pkg.code}): {installed_pkg.text.strip()}",
                    partial(),
                    abi,
                )

    avd_home.mkdir(parents=True, exist_ok=True)
    for profile in missing_profiles:
        avd_dir = avd_home / f"{profile.name}.avd"
        created = _run(
            runner,
            [
                str(avdmanager),
                "create",
                "avd",
                "--name",
                profile.name,
                "--package",
                profile.package(abi),
                "--device",
                profile.device,
                "--path",
                str(avd_dir),
            ],
            "no\n",
            180,
        )
        if created.code != 0:
            return _fail(
                f"avdmanager create {profile.name} failed ({created.code}): {created.text.strip()}",
                partial(),
                abi,
            )
        if profile.hardware_updates():
            config = avd_dir / "config.ini"
            if not config.is_file():
                return _fail(f"{profile.name} was created but {config} is missing.", partial(), abi)
            config.write_text(apply_hardware(config.read_text(encoding="utf-8"), profile), encoding="utf-8")
        done[profile.name] = _outcome(profile, "created", abi)
    return Report(outcomes=tuple(partial()), abi=abi)


def ensure_from_host(
    runner: Runner = run_command,
    *,
    machine: str | None = None,
    env: Mapping[str, str] | None = None,
    home: Path | None = None,
    platform_name: str | None = None,
) -> Report:
    env = os.environ if env is None else env
    platform_name = sys.platform if platform_name is None else platform_name
    home = Path.home() if home is None else home
    machine = platform.machine() if machine is None else machine
    return ensure(
        sdkmanager=locate_tool("sdkmanager", env, platform_name, home),
        avdmanager=locate_tool("avdmanager", env, platform_name, home),
        runner=runner,
        machine=machine,
        avd_home=avd_home_dir(env, home),
    )


def _outcome(profile: Profile, action: Action, abi: str) -> Outcome:
    return Outcome(
        name=profile.name,
        action=action,
        device=profile.device,
        api=profile.api,
        abi=abi,
        package=profile.package(abi),
        ram_mb=profile.ram_mb,
    )


def to_json(report: Report) -> str:
    payload = {
        "ok": report.ok,
        "abi": report.abi,
        "install": report.install,
        "error": report.error,
        "profiles": [
            {
                "name": item.name,
                "action": item.action,
                "device": item.device,
                "api": item.api,
                "abi": item.abi,
                "package": item.package,
                "ram_mb": item.ram_mb,
            }
            for item in report.outcomes
        ],
    }
    return json.dumps(payload, indent=2)


def to_table(report: Report) -> str:
    lines = [f"{'NAME':<16} {'ACTION':<8} {'DEVICE':<12} PACKAGE"]
    for item in report.outcomes:
        lines.append(f"{item.name:<16} {item.action:<8} {item.device:<12} {item.package}")
    if report.error:
        lines.append(f"ERROR android-avd: {report.error}")
    elif report.ok:
        lines.append("android-avd: ok")
    return "\n".join(lines)
