"""CLI for the geodata pipeline. `geodata fetch` downloads and verifies pinned sources."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from warroom_geodata.sources import Opener, SourceError, fetch_source, load_manifest, open_https


def repo_root() -> Path:
    starts = [Path.cwd(), Path(__file__).resolve()]
    for start in starts:
        for candidate in [start, *start.parents]:
            if (candidate / "AGENTS.md").is_file() and (candidate / "backlog").is_dir():
                return candidate
    raise SourceError(".", "could not find the War Room repo root (AGENTS.md and backlog/)")


def run(argv: list[str] | None = None, opener: Opener | None = None) -> int:
    parser = argparse.ArgumentParser(prog="geodata", description="War Room geodata pipeline")
    sub = parser.add_subparsers(dest="cmd", required=True)
    fetch = sub.add_parser("fetch", help="download pinned sources and verify SHA-256")
    fetch.add_argument("--manifest", type=Path, help="sources.lock.yaml (default: tools/geodata/sources.lock.yaml)")
    fetch.add_argument("--cache", type=Path, help="cache directory (default: artifacts/geodata/raw)")
    fetch.add_argument("--json", action="store_true", help="print a JSON object")
    args = parser.parse_args(argv)

    try:
        manifest = args.manifest
        cache = args.cache
        if manifest is None or cache is None:
            root = repo_root()
            manifest = manifest or root / "tools" / "geodata" / "sources.lock.yaml"
            cache = cache or root / "artifacts" / "geodata" / "raw"
        results = [fetch_source(source, cache, opener or open_https) for source in load_manifest(manifest)]
    except SourceError as exc:
        _emit_error(args.json, exc)
        return 1

    payload = {
        "ok": True,
        "results": [
            {"id": item.id, "path": str(item.path), "sha256": item.sha256, "cached": item.cached} for item in results
        ],
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    elif results:
        for item in results:
            state = "cached" if item.cached else "fetched"
            print(f"{state} {item.id} {item.path}")
    else:
        print("no sources in manifest")
    return 0


def _emit_error(as_json: bool, exc: SourceError) -> None:
    if as_json:
        print(json.dumps({"ok": False, "error": f"{exc.where}: {exc.message}"}))
    else:
        print(f"ERROR {exc}", file=sys.stderr)


def main(argv: list[str] | None = None) -> None:
    sys.exit(run(argv))
