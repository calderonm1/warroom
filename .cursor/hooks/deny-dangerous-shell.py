#!/usr/bin/env python3
"""Fail-closed gate for agent shell commands (ST-01.3.5, ST-01.3.6).

Literal ``git push`` / ``terraform apply`` / ``gh pr merge`` sequences are denied, and so
are the ordinary forms those regexes miss: git global options (``-C``), force refspecs
(``+main``), quoted refs, ``--all`` / ``--mirror``, ``terraform -chdir``, and ``gh -R``.
"""

from __future__ import annotations

import json
import re
import shlex
import sys

DENY_GH_MERGE = re.compile(r"\bgh\s+pr\s+merge\b", re.I)
DENY_TF = re.compile(r"\bterraform\s+(apply|destroy)\b", re.I)
PUSH = re.compile(r"\bgit\s+push\b", re.I)
# Destination is main/master (remote-qualified, refspec, or bare).
MAIN_DEST = re.compile(
    r"(?:^|[\s:])(?:origin/)?(?:heads/)?(?:refs/heads/)?(main|master)(?:\s|$)",
    re.I,
)

_MERGE = "Blocked: agents must not merge pull requests (CONV-GIT-007)."
_TERRAFORM = "Blocked: terraform apply/destroy is not allowed from agent shells."
_PUSH = "Blocked: do not push or force-push to main/master; open a PR instead."
_UNPARSED = "Blocked: hook could not parse the command safely."

_WRAPPERS = {"sudo", "command", "env", "nice", "nohup", "time"}
_SHELLS = {"bash", "sh", "zsh", "dash", "ksh", "ash"}
_WRAPPER_ARGS = {
    "sudo": {"-u", "-g", "-C", "-D", "-h", "-p", "-r", "--user", "--group", "--chdir", "--prompt", "--role"},
    "env": {"-u", "--unset", "-C", "--chdir"},
    "nice": {"-n", "--adjustment"},
    "command": set(),
    "nohup": set(),
    "time": set(),
}
_GIT_GLOBAL_ARGS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--super-prefix", "--config-env"}
_PUSH_ARGS = {"-o", "--push-option", "--receive-pack", "--exec", "--repo", "--recurse-submodules"}
_GH_ARGS = {"-R", "--repo", "--hostname", "--jq", "--template", "--cache"}
_PROTECTED = {"main", "master"}
_MAX_DEPTH = 6


def decide(command: str) -> tuple[str, str]:
    """Return (permission, agent_message). permission is allow or deny."""
    text = command.strip()
    if not text:
        return "allow", ""
    if DENY_GH_MERGE.search(text):
        return "deny", _MERGE
    if DENY_TF.search(text):
        return "deny", _TERRAFORM
    if PUSH.search(text) and MAIN_DEST.search(text):
        return "deny", _PUSH
    reason = _scan(text, 0)
    if reason == "merge":
        return "deny", _MERGE
    if reason == "terraform":
        return "deny", _TERRAFORM
    if reason == "push":
        return "deny", _PUSH
    if reason == "unparsed":
        return "deny", _UNPARSED
    return "allow", ""


def _scan(text: str, depth: int) -> str | None:
    if depth > _MAX_DEPTH:
        return "unparsed"
    reasons: list[str] = []
    for segment in _split_segments(text):
        try:
            tokens = shlex.split(segment, posix=True, comments=False)
        except ValueError:
            return "unparsed"
        reason = _classify(_strip_comment(tokens), depth)
        if reason:
            reasons.append(reason)
        for inner in _substitutions(segment):
            nested = _scan(inner, depth + 1)
            if nested:
                reasons.append(nested)
    for kind in ("unparsed", "merge", "terraform", "push"):
        if kind in reasons:
            return kind
    return None


def _classify(tokens: list[str], depth: int) -> str | None:
    tokens = _unwrap(tokens)
    if not tokens:
        return None
    name = _basename(tokens[0])
    reasons: list[str] = []
    for script in _shell_scripts(name, tokens):
        nested = _scan(script, depth + 1)
        if nested:
            reasons.append(nested)
    if name == "gh" and _gh_pr_merge(tokens):
        reasons.append("merge")
    elif name == "terraform" and _terraform_mutate(tokens):
        reasons.append("terraform")
    elif name == "git" and _git_push_protected(tokens):
        reasons.append("push")
    for kind in ("unparsed", "merge", "terraform", "push"):
        if kind in reasons:
            return kind
    return None


def _split_segments(text: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    quote: str | None = None
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if quote == "'":
            buf.append(ch)
            if ch == "'":
                quote = None
            i += 1
            continue
        if quote == '"':
            buf.append(ch)
            if ch == "\\" and i + 1 < n:
                buf.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                quote = None
            i += 1
            continue
        if ch in {"'", '"'}:
            quote = ch
            buf.append(ch)
            i += 1
            continue
        if ch in {"\n", ";"} or text.startswith("&&", i) or text.startswith("||", i):
            parts.append("".join(buf))
            buf = []
            i += 2 if text.startswith(("&&", "||"), i) else 1
            continue
        if ch in {"&", "|"}:
            parts.append("".join(buf))
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    parts.append("".join(buf))
    return [part.strip() for part in parts if part.strip()]


def _substitutions(text: str) -> list[str]:
    found: list[str] = []
    i = 0
    while i < len(text):
        if text.startswith("$(", i):
            depth = 1
            j = i + 2
            while j < len(text) and depth:
                if text.startswith("$(", j):
                    depth += 1
                    j += 2
                    continue
                if text[j] == ")":
                    depth -= 1
                j += 1
            if depth == 0:
                found.append(text[i + 2 : j - 1])
            i = j
            continue
        if text[i] == "`":
            j = text.find("`", i + 1)
            if j == -1:
                break
            found.append(text[i + 1 : j])
            i = j + 1
            continue
        i += 1
    return found


def _strip_comment(tokens: list[str]) -> list[str]:
    for index, token in enumerate(tokens):
        if token.startswith("#"):
            return tokens[:index]
    return tokens


def _basename(token: str) -> str:
    name = token.replace("\\", "/").rsplit("/", 1)[-1].lower()
    return name[:-4] if name.endswith(".exe") else name


def _unwrap(tokens: list[str]) -> list[str]:
    while tokens:
        if "=" in tokens[0] and not tokens[0].startswith("-"):
            tokens = tokens[1:]
            continue
        name = _basename(tokens[0])
        if name not in _WRAPPERS:
            break
        tokens = tokens[_skip_flags(tokens, 1, _WRAPPER_ARGS[name]) :]
    return tokens


def _skip_flags(tokens: list[str], index: int, with_arg: set[str]) -> int:
    while index < len(tokens):
        token = tokens[index]
        if token == "--":
            return index + 1
        if token.startswith("--") and "=" in token:
            index += 1
            continue
        if token in with_arg or (token.startswith("-C") and token != "-C"):
            index += 2 if token in with_arg else 1
            continue
        if token.startswith("-"):
            index += 1
            continue
        break
    return index


def _shell_scripts(name: str, tokens: list[str]) -> list[str]:
    if name == "eval":
        return [" ".join(tokens[1:])] if len(tokens) > 1 else []
    if name not in _SHELLS:
        return []
    index = 1
    while index < len(tokens):
        token = tokens[index]
        if token == "-c" and index + 1 < len(tokens):
            return [tokens[index + 1]]
        if token.startswith("-") and not token.startswith("--") and "c" in token[1:]:
            return [tokens[index + 1]] if index + 1 < len(tokens) else []
        if token.startswith("-"):
            index += 1
            continue
        break
    return []


def _gh_pr_merge(tokens: list[str]) -> bool:
    index = _skip_flags(tokens, 1, _GH_ARGS)
    if index >= len(tokens) or _basename(tokens[index]) != "pr":
        return False
    index = _skip_flags(tokens, index + 1, _GH_ARGS)
    return index < len(tokens) and tokens[index].lower() == "merge"


def _terraform_mutate(tokens: list[str]) -> bool:
    index = 1
    while index < len(tokens):
        token = tokens[index]
        if token == "--":
            index += 1
            break
        if token.startswith("-chdir=") or token in {"-help", "-version", "--help", "--version"}:
            index += 1
            continue
        if token == "-chdir":
            index += 2
            continue
        if token.startswith("-"):
            index += 1
            continue
        break
    return index < len(tokens) and tokens[index].lower() in {"apply", "destroy"}


def _git_push_protected(tokens: list[str]) -> bool:
    index = _skip_flags(tokens, 1, _GIT_GLOBAL_ARGS)
    if index >= len(tokens) or tokens[index].lower() != "push":
        return False
    index += 1
    has_repo = False
    push_all = False
    positionals: list[str] = []
    while index < len(tokens):
        token = tokens[index]
        if token == "--":
            positionals.extend(tokens[index + 1 :])
            break
        flag = token.split("=", 1)[0] if token.startswith("--") and "=" in token else token
        if flag in {"--all", "--mirror"}:
            push_all = True
            index += 1
            continue
        if token.startswith("--") and "=" in token:
            if flag == "--repo":
                has_repo = True
            index += 1
            continue
        if token in _PUSH_ARGS:
            if token == "--repo":
                has_repo = True
            index += 2
            continue
        if token.startswith("-"):
            index += 1
            continue
        positionals.append(token)
        index += 1
    if push_all:
        return True
    refspecs = positionals if has_repo else positionals[1:]
    return any(_targets_protected(refspec) for refspec in refspecs)


def _targets_protected(refspec: str) -> bool:
    ref = refspec[1:] if refspec.startswith("+") else refspec
    destination = ref.split(":", 1)[1] if ":" in ref else ref
    lowered = destination.lower()
    for prefix in ("refs/heads/", "heads/"):
        if lowered.startswith(prefix):
            lowered = lowered[len(prefix) :]
            break
    return lowered in _PROTECTED


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        print(json.dumps({"permission": "deny", "agent_message": "Blocked: hook input was not JSON."}))
        return 0
    command = payload.get("command") or ""
    if not isinstance(command, str):
        command = ""
    permission, message = decide(command)
    out: dict[str, str] = {"permission": permission}
    if message:
        out["agent_message"] = message
        out["user_message"] = message
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
