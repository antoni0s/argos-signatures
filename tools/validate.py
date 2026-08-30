#!/usr/bin/env python3

import hashlib
import json
import re
import sys
from pathlib import Path

CHANNELS = ("stable", "testing")
SAFE_NAME = re.compile(r"^[A-Za-z0-9._-]+$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_db(path: Path) -> None:
    data = path.read_bytes()
    if b"\x00" in data:
        fail(f"{path}: NUL byte found")

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        fail(f"{path}: not valid UTF-8 ({exc})")

    for line_no, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "|" not in line:
            fail(f"{path}:{line_no}: active signature line has no pipe delimiter")


def validate_channel(root: Path, channel: str) -> None:
    channel_dir = root / channel
    manifest_path = channel_dir / "manifest.json"
    signatures_dir = channel_dir / "signatures"

    if not manifest_path.is_file():
        fail(f"missing {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if manifest.get("schema_version") != 1:
        fail(f"{manifest_path}: unsupported schema_version")
    if manifest.get("channel") != channel:
        fail(f"{manifest_path}: channel field must be {channel!r}")
    if not isinstance(manifest.get("database_version"), str) or not manifest["database_version"].strip():
        fail(f"{manifest_path}: invalid database_version")

    files = manifest.get("files")
    if not isinstance(files, dict):
        fail(f"{manifest_path}: files must be an object")

    actual_files = set()
    if signatures_dir.exists():
        actual_files = {
            p.name for p in signatures_dir.iterdir()
            if p.is_file() and p.name != ".gitkeep"
        }

    declared_files = set(files)
    if actual_files != declared_files:
        missing = sorted(declared_files - actual_files)
        extra = sorted(actual_files - declared_files)
        if missing:
            print(f"Missing files in {channel}: {', '.join(missing)}", file=sys.stderr)
        if extra:
            print(f"Unexpected files in {channel}: {', '.join(extra)}", file=sys.stderr)
        fail(f"{channel}: manifest/file set mismatch")

    for name, meta in files.items():
        if not SAFE_NAME.fullmatch(name) or name in {".", ".."}:
            fail(f"{manifest_path}: unsafe filename {name!r}")
        if not isinstance(meta, dict):
            fail(f"{manifest_path}: metadata for {name} must be an object")

        expected_hash = meta.get("sha256")
        expected_size = meta.get("size")
        if not isinstance(expected_hash, str) or not SHA256.fullmatch(expected_hash):
            fail(f"{manifest_path}: invalid SHA-256 for {name}")
        if not isinstance(expected_size, int) or expected_size < 0:
            fail(f"{manifest_path}: invalid size for {name}")

        path = signatures_dir / name
        if path.stat().st_size != expected_size:
            fail(f"{path}: size mismatch")
        if sha256_file(path) != expected_hash:
            fail(f"{path}: SHA-256 mismatch")
        validate_db(path)

    print(f"{channel}: PASS ({len(files)} files, database_version={manifest['database_version']})")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    for channel in CHANNELS:
        validate_channel(root, channel)
    print("Argos signature repository validation: PASS")


if __name__ == "__main__":
    main()
