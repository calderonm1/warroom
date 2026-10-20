"""Fetch pinned geodata sources and verify them with SHA-256 (GEO-006)."""

from __future__ import annotations

import hashlib
import os
import re
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO
from urllib.parse import urlsplit

import yaml

# Safety cap when a manifest entry omits max_bytes. Override per source for larger rasters.
DEFAULT_MAX_BYTES = 512 * 1024 * 1024
_READ_CHUNK = 1024 * 1024
_TIMEOUT_SECONDS = 120

_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
_VERSION = re.compile(r"^[A-Za-z0-9._+-]{1,64}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_FILENAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,200}$")

_TOP_KEYS = {"version", "sources"}
_SOURCE_KEYS = {"id", "version", "url", "sha256", "filename", "max_bytes"}

Opener = Callable[[str], BinaryIO]


class SourceError(Exception):
    """A manifest entry or download failed verification."""

    def __init__(self, where: str, message: str) -> None:
        self.where = where
        self.message = message
        super().__init__(f"{where}: {message}")


@dataclass(frozen=True)
class Source:
    id: str
    version: str
    url: str
    sha256: str
    filename: str
    max_bytes: int


@dataclass(frozen=True)
class FetchResult:
    id: str
    path: Path
    sha256: str
    cached: bool


class HttpsOnlyRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Refuse redirects that leave HTTPS."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not _is_https(newurl):
            raise SourceError(req.full_url, "redirect is not https")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def load_manifest(path: Path) -> list[Source]:
    """Load `sources.lock.yaml`. An empty `sources` list is valid."""
    if not path.is_file():
        raise SourceError(str(path), "manifest not found")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise SourceError(str(path), f"invalid YAML: {' '.join(str(exc).split())}") from exc
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise SourceError(str(path), "manifest must be a mapping")
    unknown = set(data) - _TOP_KEYS
    if unknown:
        raise SourceError(str(path), f"unknown keys: {', '.join(sorted(unknown))}")
    if data.get("version") != 1:
        raise SourceError(str(path), f"unsupported manifest version {data.get('version')!r}")
    raw_sources = data.get("sources", [])
    if not isinstance(raw_sources, list):
        raise SourceError(str(path), "sources must be a list")

    sources: list[Source] = []
    seen: set[str] = set()
    for index, raw in enumerate(raw_sources):
        where = f"{path}:sources[{index}]"
        source = _parse_source(where, raw)
        if source.id in seen:
            raise SourceError(where, f"duplicate source id {source.id!r}")
        seen.add(source.id)
        sources.append(source)
    return sources


def fetch_source(source: Source, cache_dir: Path, opener: Opener) -> FetchResult:
    """Return the cached file for `source`, downloading it when the hash is missing or wrong."""
    dest = cache_dir.resolve() / source.sha256 / source.filename
    if dest.exists() and not dest.is_file():
        raise SourceError(str(dest), "cache path is not a file")
    if dest.is_file() and _sha256_file(dest) == source.sha256:
        return FetchResult(source.id, dest, source.sha256, cached=True)
    if dest.is_file():
        dest.unlink()
    try:
        _download_to(source, dest, opener)
    except SourceError:
        raise
    except urllib.error.URLError as exc:
        raise SourceError(source.url, f"download failed: {exc}") from exc
    return FetchResult(source.id, dest, source.sha256, cached=False)


def open_https(url: str) -> BinaryIO:
    """Open an HTTPS URL. Redirects to non-HTTPS are errors."""
    if not _is_https(url):
        raise SourceError(url, "source URL must be https")
    opener = urllib.request.build_opener(HttpsOnlyRedirectHandler)
    try:
        return opener.open(url, timeout=_TIMEOUT_SECONDS)
    except SourceError:
        raise
    except urllib.error.URLError as exc:
        raise SourceError(url, f"download failed: {exc}") from exc


def _parse_source(where: str, raw: object) -> Source:
    if not isinstance(raw, dict):
        raise SourceError(where, "source must be a mapping")
    unknown = set(raw) - _SOURCE_KEYS
    if unknown:
        raise SourceError(where, f"unknown keys: {', '.join(sorted(unknown))}")
    source_id = _require_match(where, raw, "id", _ID, "lowercase id (letters, digits, hyphens)")
    version = _require_match(where, raw, "version", _VERSION, "version string")
    url = raw.get("url")
    if not isinstance(url, str) or not _is_https(url) or len(url) > 2048:
        raise SourceError(where, "url must be an https URL")
    sha256 = _require_match(where, raw, "sha256", _SHA256, "lowercase sha256 hex")
    filename = _require_match(where, raw, "filename", _FILENAME, "plain filename")
    max_bytes = raw.get("max_bytes", DEFAULT_MAX_BYTES)
    if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or max_bytes < 1:
        raise SourceError(where, "max_bytes must be a positive integer")
    return Source(source_id, version, url, sha256, filename, max_bytes)


def _require_match(where: str, raw: dict, key: str, pattern: re.Pattern[str], label: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or pattern.fullmatch(value) is None:
        raise SourceError(where, f"{key} must be a {label}")
    return value


def _is_https(url: str) -> bool:
    parts = urlsplit(url)
    return parts.scheme == "https" and bool(parts.hostname)


def _sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(_READ_CHUNK), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _download_to(source: Source, dest: Path, opener: Opener) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    partial = dest.with_name(f".{dest.name}.partial")
    hasher = hashlib.sha256()
    total = 0
    try:
        with opener(source.url) as fh, partial.open("wb") as out:
            while chunk := fh.read(_READ_CHUNK):
                total += len(chunk)
                if total > source.max_bytes:
                    raise SourceError(source.url, f"download exceeds max_bytes ({source.max_bytes})")
                hasher.update(chunk)
                out.write(chunk)
        digest = hasher.hexdigest()
        if digest != source.sha256:
            raise SourceError(source.url, f"sha256 mismatch: expected {source.sha256}, got {digest}")
        os.replace(partial, dest)
    except Exception:
        partial.unlink(missing_ok=True)
        raise
