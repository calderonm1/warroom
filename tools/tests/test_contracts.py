"""ST-07.1.1: realtime protobuf contracts and buf rules."""

from __future__ import annotations

import re
from pathlib import Path

REAL_ROOT = Path(__file__).resolve().parents[2]
PROTO_DIR = REAL_ROOT / "shared" / "contracts" / "proto" / "warroom" / "realtime" / "v1"
BUF_YAML = REAL_ROOT / "shared" / "contracts" / "buf.yaml"

REQUIRED_MESSAGES = (
    "ClientEnvelope",
    "ServerEnvelope",
    "Hello",
    "Welcome",
    "SubscribeMatch",
    "CommandSubmit",
    "CommandAck",
    "CommandRejected",
    "Error",
    "MatchSnapshot",
    "StateDelta",
)


def _proto_text() -> str:
    files = sorted(PROTO_DIR.glob("*.proto"))
    assert files, f"no proto files in {PROTO_DIR}"
    return "\n".join(path.read_text(encoding="utf-8") for path in files)


def test_realtime_v1_defines_envelope_handshake_command_ack_error_and_update():
    text = _proto_text()
    for name in REQUIRED_MESSAGES:
        assert re.search(rf"^message {name} \{{", text, re.MULTILINE), name
    assert "package warroom.realtime.v1;" in text
    assert "google.protobuf.Timestamp" not in text
    assert "ERROR_CODE_UNSPECIFIED = 0;" in text
    assert "ERROR_CODE_UPGRADE_REQUIRED" in text


def test_buf_yaml_declares_lint_and_breaking_rules():
    text = BUF_YAML.read_text(encoding="utf-8")
    assert "lint:" in text
    assert "STANDARD" in text
    assert "breaking:" in text
    assert "FILE" in text


def test_makefile_contracts_lint_is_part_of_check():
    makefile = (REAL_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "contracts-lint:" in makefile
    check = next(line for line in makefile.splitlines() if line.startswith("check:"))
    assert "contracts-lint" in check
