"""ST-02.5.1: scripted Android emulator profiles."""

from __future__ import annotations

import json
import stat
from pathlib import Path

import pytest
from conftest import REAL_ROOT

from warroom_tools import android_avd, cli

INSTALL = "docs/06-environments/device-testing.md#4-android-emulator-profiles"
DEVICE_LIST = """id: 17 or "pixel_8"
    Name: Pixel 8
    OEM : Google
---------
id: 48 or "small_phone"
    Name: Small Phone
    OEM : Google
"""


def _result(code: int = 0, out: str = "", err: str = "") -> android_avd.CmdResult:
    return android_avd.CmdResult(code, out, err)


def test_device_testing_doc_lists_install_and_launch_for_each_avd():
    text = (REAL_ROOT / "docs/06-environments/device-testing.md").read_text(encoding="utf-8")
    assert android_avd.INSTALL_DOC == INSTALL
    assert INSTALL.split("#", 1)[1] in text or "## 4. Android emulator profiles" in text
    for name in ("wr_pixel_api35", "wr_small_api29"):
        assert name in text
        assert f"emulator -avd {name}" in text
    assert "make android-avd" in text
    assert "adb install -r" in text
    assert "Build And Run" in text
    assert "OQ-009" in text
    makefile = (REAL_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "android-avd:" in makefile
    assert "$(WR) android-avd" in makefile


def test_abi_follows_the_host_cpu():
    assert android_avd.abi_for_machine("arm64") == "arm64-v8a"
    assert android_avd.abi_for_machine("aarch64") == "arm64-v8a"
    assert android_avd.abi_for_machine("x86_64") == "x86_64"
    assert android_avd.abi_for_machine("AMD64") == "x86_64"
    pixel = android_avd.PROFILES[0]
    assert pixel.package("arm64-v8a") == "system-images;android-35;google_apis;arm64-v8a"
    assert android_avd.PROFILES[1].package("x86_64") == "system-images;android-29;google_apis;x86_64"


def test_hardware_patch_sets_pixel_ram_and_gpu_and_leaves_other_keys():
    original = "hw.keyboard=no\nhw.ramSize=2048\n"
    patched = android_avd.apply_hardware(original, android_avd.PROFILES[0])
    assert "hw.keyboard=no" in patched
    assert "hw.ramSize=4096" in patched
    assert "hw.gpu.enabled=yes" in patched
    assert "hw.gpu.mode=host" in patched
    assert patched.count("hw.ramSize=") == 1
    assert android_avd.apply_hardware(original, android_avd.PROFILES[1]) == original


def test_existing_avds_are_not_recreated(tmp_path: Path):
    calls: list[tuple[tuple[str, ...], str | None]] = []

    def runner(argv, stdin=None, timeout=60):
        calls.append((tuple(argv), stdin))
        return _result(out="    Name: wr_pixel_api35\n    Name: wr_small_api29\n")

    report = android_avd.ensure(
        sdkmanager=tmp_path / "sdkmanager",
        avdmanager=tmp_path / "avdmanager",
        runner=runner,
        machine="x86_64",
        avd_home=tmp_path / "avd",
    )
    assert report.ok
    assert [item.action for item in report.outcomes] == ["exists", "exists"]
    assert len(calls) == 1
    assert calls[0][0][1:] == ("list", "avd")
    assert "sdkmanager" not in calls[0][0][0]


def test_missing_avds_are_created_with_host_abi_and_pixel_hardware(tmp_path: Path):
    avd_home = tmp_path / "avd"
    calls: list[tuple[str, ...]] = []

    def runner(argv, stdin=None, timeout=60):
        calls.append(tuple(argv))
        command = argv[1:]
        if command[:2] == ["list", "avd"]:
            return _result(out="Available Android Virtual Devices:\n")
        if command[:2] == ["list", "device"]:
            return _result(out=DEVICE_LIST)
        if command[:1] == ["--list_installed"]:
            return _result(out="Installed packages:\n")
        if command[:1] == ["--licenses"]:
            assert stdin is not None and stdin.startswith("y")
            return _result()
        if command[:1] == ["--install"]:
            return _result()
        if command[:2] == ["create", "avd"]:
            assert stdin == "no\n"
            path = Path(command[command.index("--path") + 1])
            path.mkdir(parents=True)
            (path / "config.ini").write_text("hw.ramSize=512\nhw.keyboard=no\n", encoding="utf-8")
            return _result()
        raise AssertionError(command)

    report = android_avd.ensure(
        sdkmanager=tmp_path / "sdkmanager",
        avdmanager=tmp_path / "avdmanager",
        runner=runner,
        machine="aarch64",
        avd_home=avd_home,
    )
    assert report.ok
    assert report.abi == "arm64-v8a"
    assert [item.action for item in report.outcomes] == ["created", "created"]
    assert [item.package for item in report.outcomes] == [
        "system-images;android-35;google_apis;arm64-v8a",
        "system-images;android-29;google_apis;arm64-v8a",
    ]
    pixel_cfg = (avd_home / "wr_pixel_api35.avd" / "config.ini").read_text(encoding="utf-8")
    small_cfg = (avd_home / "wr_small_api29.avd" / "config.ini").read_text(encoding="utf-8")
    assert "hw.ramSize=4096" in pixel_cfg
    assert "hw.gpu.mode=host" in pixel_cfg
    assert "hw.keyboard=no" in pixel_cfg
    assert small_cfg == "hw.ramSize=512\nhw.keyboard=no\n"
    joined = " ".join(" ".join(call) for call in calls)
    assert "--install system-images;android-35;google_apis;arm64-v8a" in joined
    assert "--device pixel_8" in joined
    assert "--device small_phone" in joined


def test_installed_system_image_skips_sdkmanager_install(tmp_path: Path):
    calls: list[tuple[str, ...]] = []

    def runner(argv, stdin=None, timeout=60):
        calls.append(tuple(argv))
        command = argv[1:]
        if command[:2] == ["list", "avd"]:
            return _result(out="    Name: wr_small_api29\n")
        if command[:2] == ["list", "device"]:
            return _result(out=DEVICE_LIST)
        if command[:1] == ["--list_installed"]:
            return _result(out="system-images;android-35;google_apis;x86_64 | 1 | image\n")
        if command[:2] == ["create", "avd"]:
            path = Path(command[command.index("--path") + 1])
            path.mkdir(parents=True)
            (path / "config.ini").write_text("AvdId=wr_pixel_api35\n", encoding="utf-8")
            return _result()
        raise AssertionError(command)

    report = android_avd.ensure(
        sdkmanager=tmp_path / "sdkmanager",
        avdmanager=tmp_path / "avdmanager",
        runner=runner,
        machine="x86_64",
        avd_home=tmp_path / "avd",
    )
    assert report.ok
    assert [(item.name, item.action) for item in report.outcomes] == [
        ("wr_pixel_api35", "created"),
        ("wr_small_api29", "exists"),
    ]
    flat = [" ".join(call[1:]) for call in calls]
    assert not any(item.startswith("--licenses") or item.startswith("--install") for item in flat)


def test_missing_tools_exit_with_the_install_section(tmp_path: Path):
    report = android_avd.ensure(
        sdkmanager=None,
        avdmanager=None,
        runner=lambda *args, **kwargs: _result(),
        machine="x86_64",
        avd_home=tmp_path,
    )
    assert report.ok is False
    assert report.error is not None
    assert "sdkmanager and avdmanager not found" in report.error
    assert INSTALL in report.error
    assert INSTALL in android_avd.to_table(report)
    payload = json.loads(android_avd.to_json(report))
    assert payload["ok"] is False
    assert payload["install"] == INSTALL


def test_unknown_device_profile_fails_before_install(tmp_path: Path):
    def runner(argv, stdin=None, timeout=60):
        command = argv[1:]
        if command[:2] == ["list", "avd"]:
            return _result(out="")
        if command[:2] == ["list", "device"]:
            return _result(out='id: 1 or "pixel_8"\n')
        raise AssertionError(command)

    report = android_avd.ensure(
        sdkmanager=tmp_path / "sdkmanager",
        avdmanager=tmp_path / "avdmanager",
        runner=runner,
        machine="x86_64",
        avd_home=tmp_path / "avd",
    )
    assert report.ok is False
    assert report.error is not None
    assert "small_phone" in report.error


def test_locate_tool_searches_android_home_before_the_default_sdk(tmp_path: Path):
    home = tmp_path / "home"
    sdk = tmp_path / "sdk"
    binary = sdk / "cmdline-tools" / "latest" / "bin" / "avdmanager"
    binary.parent.mkdir(parents=True)
    binary.write_text("#!/bin/sh\n", encoding="utf-8")
    found = android_avd.locate_tool(
        "avdmanager",
        {"ANDROID_HOME": str(sdk), "PATH": str(tmp_path / "empty-path")},
        "linux",
        home,
    )
    assert found == binary


def test_host_scripts_create_both_profiles_then_skip_them(tmp_path: Path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "calls.log"
    avd_home = tmp_path / "avds"
    _write_executable(
        bin_dir / "sdkmanager",
        f"""#!/bin/sh
printf '%s\\n' "$*" >> "{log}"
exit 0
""",
    )
    _write_executable(
        bin_dir / "avdmanager",
        f"""#!/bin/sh
printf '%s\\n' "$*" >> "{log}"
if [ "$1" = "list" ] && [ "$2" = "avd" ]; then
  echo "Available Android Virtual Devices:"
  for dir in "{avd_home}"/*.avd; do
    [ -d "$dir" ] || continue
    base=$(basename "$dir" .avd)
    echo "    Name: $base"
  done
  exit 0
fi
if [ "$1" = "list" ] && [ "$2" = "device" ]; then
  echo 'id: 17 or "pixel_8"'
  echo 'id: 48 or "small_phone"'
  exit 0
fi
if [ "$1" = "create" ]; then
  path=""
  while [ $# -gt 0 ]; do
    if [ "$1" = "--path" ]; then
      path="$2"
    fi
    shift
  done
  mkdir -p "$path"
  printf '%s\\n' "hw.ramSize=512" > "$path/config.ini"
  exit 0
fi
exit 1
""",
    )
    env = {
        "PATH": str(bin_dir),
        "ANDROID_AVD_HOME": str(avd_home),
        "HOME": str(tmp_path / "home"),
    }
    first = android_avd.ensure_from_host(env=env, machine="x86_64", home=tmp_path / "home", platform_name="linux")
    assert first.ok
    assert [item.action for item in first.outcomes] == ["created", "created"]
    pixel = (avd_home / "wr_pixel_api35.avd" / "config.ini").read_text(encoding="utf-8")
    assert "hw.ramSize=4096" in pixel
    assert "hw.gpu.mode=host" in pixel
    small = (avd_home / "wr_small_api29.avd" / "config.ini").read_text(encoding="utf-8")
    assert small == "hw.ramSize=512\n"
    log_before = log.read_text(encoding="utf-8")
    second = android_avd.ensure_from_host(env=env, machine="x86_64", home=tmp_path / "home", platform_name="linux")
    assert second.ok
    assert [item.action for item in second.outcomes] == ["exists", "exists"]
    log_after = log.read_text(encoding="utf-8")
    assert log_after.count("create avd") == log_before.count("create avd") == 2


def test_cli_json_reports_a_missing_sdk(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    monkeypatch.setattr(
        android_avd,
        "ensure_from_host",
        lambda: android_avd.Report(outcomes=(), abi="x86_64", error=f"sdkmanager not found. See {INSTALL}."),
    )
    code = cli.main(["android-avd", "--json"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert code == 1
    assert payload["ok"] is False
    assert payload["install"] == INSTALL


def test_parse_installed_packages_ignores_the_available_section():
    text = """Installed packages:
  system-images;android-35;google_apis;x86_64 | 1 | image
Available Packages:
  system-images;android-29;google_apis;x86_64 | 1 | image
"""
    assert android_avd.parse_installed_packages(text) == {"system-images;android-35;google_apis;x86_64"}


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)


def test_real_command_without_sdk_names_the_doc(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    """A machine with no Android SDK must fail closed and name the install section."""

    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("PATH", str(tmp_path / "empty-path"))
    monkeypatch.delenv("ANDROID_HOME", raising=False)
    monkeypatch.delenv("ANDROID_SDK_ROOT", raising=False)
    monkeypatch.setattr(Path, "home", lambda: home)
    code = cli.main(["android-avd"])
    captured = capsys.readouterr()
    assert code == 1
    assert "sdkmanager and avdmanager not found" in captured.out
    assert INSTALL in captured.out
