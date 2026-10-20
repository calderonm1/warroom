"""ST-10.1.1: pinned geodata downloads are cached and verified with SHA-256 (GEO-006)."""

from __future__ import annotations

import hashlib
import io
import json
import urllib.request
from pathlib import Path

import pytest
import yaml

from warroom_geodata.cli import run
from warroom_geodata.sources import (
    DEFAULT_MAX_BYTES,
    HttpsOnlyRedirectHandler,
    SourceError,
    fetch_source,
    load_manifest,
)

REPO = Path(__file__).resolve().parents[3]
EMPTY_SHA = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def _files(root: Path) -> list[Path]:
    return [path for path in root.rglob("*") if path.is_file()]


def _manifest(path: Path, sources: list[dict]) -> Path:
    path.write_text(yaml.safe_dump({"version": 1, "sources": sources}), encoding="utf-8")
    return path


def _source(**overrides: object) -> dict:
    payload = b"abc"
    base = {
        "id": "sample-coast",
        "version": "1.0.0",
        "url": "https://example.com/coast.bin",
        "sha256": hashlib.sha256(payload).hexdigest(),
        "filename": "coast.bin",
    }
    base.update(overrides)
    return base


class _Opener:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload
        self.calls = 0

    def __call__(self, url: str) -> io.BytesIO:
        self.calls += 1
        return io.BytesIO(self.payload)


def test_committed_manifest_loads_and_starts_empty():
    sources = load_manifest(REPO / "tools" / "geodata" / "sources.lock.yaml")
    assert sources == []


def test_fetch_caches_and_skips_second_download(tmp_path: Path):
    payload = b"abc"
    opener = _Opener(payload)
    source = load_manifest(_manifest(tmp_path / "sources.lock.yaml", [_source()]))[0]
    cache = tmp_path / "raw"

    first = fetch_source(source, cache, opener)
    second = fetch_source(source, cache, opener)

    assert opener.calls == 1
    assert first.cached is False
    assert second.cached is True
    assert first.path == cache.resolve() / source.sha256 / "coast.bin"
    assert first.path.read_bytes() == payload
    assert second.path.read_bytes() == payload


def test_hash_mismatch_raises_and_leaves_no_cache_file(tmp_path: Path):
    source = load_manifest(_manifest(tmp_path / "sources.lock.yaml", [_source()]))[0]
    opener = _Opener(b"nope")
    cache = tmp_path / "raw"

    with pytest.raises(SourceError, match="sha256 mismatch"):
        fetch_source(source, cache, opener)

    assert _files(cache) == []


def test_corrupt_cache_is_downloaded_again(tmp_path: Path):
    payload = b"abc"
    opener = _Opener(payload)
    source = load_manifest(_manifest(tmp_path / "sources.lock.yaml", [_source()]))[0]
    cache = tmp_path / "raw"
    fetch_source(source, cache, opener)
    cached = cache.resolve() / source.sha256 / "coast.bin"
    cached.write_bytes(b"corrupt")

    again = fetch_source(source, cache, opener)

    assert opener.calls == 2
    assert again.cached is False
    assert cached.read_bytes() == payload


def test_download_over_max_bytes_is_rejected(tmp_path: Path):
    source = load_manifest(_manifest(tmp_path / "sources.lock.yaml", [_source(max_bytes=2, sha256=EMPTY_SHA)]))[0]
    cache = tmp_path / "raw"

    with pytest.raises(SourceError, match="max_bytes"):
        fetch_source(source, cache, _Opener(b"abcd"))

    assert _files(cache) == []


def test_omitted_max_bytes_uses_default(tmp_path: Path):
    source = load_manifest(_manifest(tmp_path / "sources.lock.yaml", [_source()]))[0]
    assert source.max_bytes == DEFAULT_MAX_BYTES


@pytest.mark.parametrize(
    ("overrides", "match"),
    [
        ({"url": "http://example.com/coast.bin"}, "https"),
        ({"filename": "../coast.bin"}, "filename"),
        ({"sha256": "ABC"}, "sha256"),
        ({"id": "Coast"}, "id"),
    ],
)
def test_manifest_rejects_unsafe_fields(tmp_path: Path, overrides: dict, match: str):
    with pytest.raises(SourceError, match=match):
        load_manifest(_manifest(tmp_path / "sources.lock.yaml", [_source(**overrides)]))


def test_duplicate_id_is_rejected(tmp_path: Path):
    entry = _source()
    with pytest.raises(SourceError, match="duplicate"):
        load_manifest(_manifest(tmp_path / "sources.lock.yaml", [entry, dict(entry)]))


def test_redirect_to_http_is_rejected():
    handler = HttpsOnlyRedirectHandler()
    request = urllib.request.Request("https://example.com/a")
    with pytest.raises(SourceError, match="redirect is not https"):
        handler.redirect_request(request, None, 302, "Found", {}, "http://example.com/b")


def test_https_redirect_is_allowed():
    handler = HttpsOnlyRedirectHandler()
    request = urllib.request.Request("https://example.com/a")
    redirected = handler.redirect_request(request, None, 302, "Found", {}, "https://example.com/b")
    assert redirected is not None
    assert redirected.full_url == "https://example.com/b"


def test_cli_json_reports_fetch_then_cache(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    payload = b"abc"
    opener = _Opener(payload)
    manifest = _manifest(tmp_path / "sources.lock.yaml", [_source()])
    cache = tmp_path / "raw"
    argv = ["fetch", "--manifest", str(manifest), "--cache", str(cache), "--json"]

    assert run(argv, opener=opener) == 0
    first = json.loads(capsys.readouterr().out)
    assert run(argv, opener=opener) == 0
    second = json.loads(capsys.readouterr().out)

    assert first["ok"] is True
    assert first["results"][0]["cached"] is False
    assert first["results"][0]["sha256"] == hashlib.sha256(payload).hexdigest()
    assert second["results"][0]["cached"] is True
    assert opener.calls == 1


def test_cli_json_error_on_bad_manifest(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    manifest = tmp_path / "sources.lock.yaml"
    manifest.write_text("version: 2\nsources: []\n", encoding="utf-8")

    code = run(["fetch", "--manifest", str(manifest), "--cache", str(tmp_path / "raw"), "--json"])
    captured = capsys.readouterr()

    assert code == 1
    assert json.loads(captured.out)["ok"] is False
    assert captured.err == ""


def test_cli_text_error_uses_error_prefix(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    manifest = tmp_path / "missing.lock.yaml"
    code = run(["fetch", "--manifest", str(manifest), "--cache", str(tmp_path / "raw")])
    captured = capsys.readouterr()

    assert code == 1
    assert captured.out == ""
    assert captured.err.startswith("ERROR ")
    assert "manifest not found" in captured.err
