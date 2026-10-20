#!/usr/bin/env python3
"""Fail-closed gate for agent shell commands (ST-01.3.5)."""

from __future__ import annotations

import json
import re
import sys

DENY_GH_MERGE = re.compile(r"\bgh\s+pr\s+merge\b", re.I)
DENY_TF = re.compile(r"\bterraform\s+(apply|destroy)\b", re.I)
PUSH = re.compile(r"\bgit\s+push\b", re.I)
# Destination is main/master (remote-qualified, refspec, or bare).
MAIN_DEST = re.compile(
    r"(?:^|[\s:])(?:origin/)?(?:heads/)?(?:refs/heads/)?(main|master)(?:\s|$)",
    re.I,
)


def decide(command: str) -> tuple[str, str]:
    """Return (permission, agent_message). permission is allow or deny."""
    text = command.strip()
    if not text:
        return "allow", ""
    if DENY_GH_MERGE.search(text):
        return "deny", "Blocked: agents must not merge pull requests (CONV-GIT-007)."
    if DENY_TF.search(text):
        return "deny", "Blocked: terraform apply/destroy is not allowed from agent shells."
    if PUSH.search(text) and MAIN_DEST.search(text):
        return "deny", "Blocked: do not push or force-push to main/master; open a PR instead."
    return "allow", ""


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        print(json.dumps({"permission": "deny", "agent_message": "Blocked: hook input was not JSON."}))
        return 0
    command = payload.get("command") or ""
    permission, message = decide(command)
    out: dict[str, str] = {"permission": permission}
    if message:
        out["agent_message"] = message
        out["user_message"] = message
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
