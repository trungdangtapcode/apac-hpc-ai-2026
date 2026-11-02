#!/usr/bin/env python3
"""Build a bounded, portable backup of the quality study's external objects.

The captured Git commit remains the source for inline files. This bundle only
contains selected manifest rows, their object index entries, scope metadata,
and the unique compressed object payloads those rows reference.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import tarfile


STUDY_PREFIX = (
    "2026-APAC-HPC-AI/qwen-experiments/quality-verification-20261102/"
)
STUDY_EXCLUDED_PREFIX = STUDY_PREFIX + "evidence/builds/"
ADDITIONAL_PREFIXES = (
    "2026-APAC-HPC-AI/qwen-experiments/"
    "mmlu-pro-local-quality-20261024/dataset/",
    "workspace/reports/ai-quality-verification-20261103/",
)
DEFAULT_ARCHIVE = Path("/home/apacsc42/apac-hpc-ai-research")
MANIFEST_REL = Path("backup/manifest.jsonl")
INDEX_NAME = "objects-index.json"
CHUNK = 4 * 1024 * 1024


def digest_stream(stream) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    while True:
        block = stream.read(CHUNK)
        if not block:
            break
        digest.update(block)
        size += len(block)
    return digest.hexdigest(), size


def safe_relative(value: str, label: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or ".." in path.parts or "\\" in value:
        raise ValueError(f"Unsafe {label}: {value!r}")
    return path.as_posix()


def selected_path(path: str) -> bool:
    parts = PurePosixPath(path).parts
    if any(p.startswith(("runtime-home", ".runtime-home")) for p in parts):
        return False
    if path.endswith((".sqsh", ".safetensors", ".gguf")):
        return False
    if path.startswith(STUDY_PREFIX):
        return not path.startswith(STUDY_EXCLUDED_PREFIX)
    return any(path.startswith(prefix) for prefix in ADDITIONAL_PREFIXES)


def read_snapshot(archive: Path, store: Path) -> tuple[str, list[dict], list[dict], dict[str, str]]:
    git_dir = archive / ".git"
    lock_path = git_dir / "research-checkpoint.lock"
    # Captures and this builder coordinate through this shared lock. Creating
    # the lock file is safe when this is the first use; it is not Git content.
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+b") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_SH)
        head = subprocess.run(
            ["git", "-C", str(archive), "rev-parse", "--verify", "HEAD"],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        ).stdout.strip()
        manifest_bytes = (archive / MANIFEST_REL).read_bytes()
        index_path = store / INDEX_NAME
        index_bytes = index_path.read_bytes()
        checksums_path = store / "SHA256SUMS"
        checksums_bytes = checksums_path.read_bytes() if checksums_path.is_file() else b""
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

    rows = [json.loads(line) for line in manifest_bytes.splitlines() if line.strip()]
    index = json.loads(index_bytes)
    checksums = {}
    for line in checksums_bytes.decode("utf-8").splitlines():
        fields = line.split(maxsplit=1)
        if len(fields) == 2:
            checksums[fields[1].lstrip("* ")] = fields[0]
    return head, rows, index, checksums


def verify_object(store: Path, row: dict, indexed: dict, checksums: dict[str, str]) -> dict:
    relative = safe_relative(row["object"], "object path")
    if not relative.startswith("objects/") or not relative.endswith(".zst"):
        raise ValueError(f"Unexpected object path for {row['sha256']}: {relative}")
    object_path = store / relative
    if object_path.is_symlink():
        raise ValueError(f"Object is a symlink: {relative}")
    before = object_path.lstat()
    if not stat.S_ISREG(before.st_mode):
        raise ValueError(f"Object is not a regular file: {relative}")

    with object_path.open("rb") as compressed:
        compressed_hash, compressed_size = digest_stream(compressed)
    expected_stored_size = indexed.get("stored_bytes")
    expected_stored_hash = checksums.get(relative)
    if expected_stored_size is None:
        raise ValueError(f"Compressed object lacks a size record: {relative}")
    if compressed_size != expected_stored_size:
        raise ValueError(f"Compressed size mismatch: {relative}")
    if expected_stored_hash is not None and compressed_hash != expected_stored_hash:
        raise ValueError(f"Compressed SHA-256 mismatch: {relative}")

    process = subprocess.Popen(
        ["zstd", "-q", "-d", "-c", str(object_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert process.stdout is not None
    content_hash, content_size = digest_stream(process.stdout)
    stderr = process.stderr.read() if process.stderr else b""
    result = process.wait()
    if result:
        raise ValueError(f"zstd decompression failed for {relative}: {stderr[:500]!r}")
    if (content_hash, content_size) != (row["sha256"], row["bytes"]):
        raise ValueError(f"Uncompressed hash/size mismatch: {relative}")

    after = object_path.lstat()
    if (before.st_ino, before.st_size, before.st_mtime_ns) != (
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
    ):
        raise ValueError(f"Object changed while being verified: {relative}")

    result_row = dict(indexed)
    result_row["stored_bytes"] = compressed_size
    result_row["stored_sha256"] = compressed_hash
    result_row["stored_sha256_origin"] = (
        "verified against retained global transport checksum"
        if expected_stored_hash is not None else
        "computed for this scoped transport; original bytes independently verified against manifest"
    )
    return result_row


def add_bytes(tar: tarfile.TarFile, name: str, payload: bytes) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(payload)
    info.mode = 0o644
    info.mtime = 0
    import io

    tar.addfile(info, io.BytesIO(payload))


def add_object(tar: tarfile.TarFile, store: Path, row: dict) -> None:
    relative = safe_relative(row["object"], "object path")
    path = store / relative
    info = tarfile.TarInfo(relative)
    current = path.lstat()
    if not stat.S_ISREG(current.st_mode) or path.is_symlink():
        raise ValueError(f"Object changed or became unsafe: {relative}")
    info.size = current.st_size
    info.mode = 0o644
    info.mtime = 0
    class HashedReader:
        def __init__(self, source):
            self.source = source
            self.digest = hashlib.sha256()
            self.size = 0

        def read(self, size=-1):
            data = self.source.read(size)
            self.digest.update(data)
            self.size += len(data)
            return data

    with path.open("rb") as source:
        reader = HashedReader(source)
        tar.addfile(info, reader)
        if (reader.digest.hexdigest(), reader.size) != (
            row["stored_sha256"],
            row["stored_bytes"],
        ):
            raise ValueError(f"Compressed object changed while bundling: {relative}")


def make_bundle(args: argparse.Namespace) -> Path:
    archive = args.archive.expanduser().resolve(strict=True)
    store_arg = args.store or archive.with_name(archive.name + "-artifacts")
    store = store_arg.expanduser().resolve(strict=True)
    out_dir = args.out_dir.expanduser().absolute()
    if out_dir.exists():
        raise FileExistsError(f"Output directory already exists: {out_dir}")
    if out_dir.is_relative_to(archive) or out_dir.is_relative_to(store):
        raise ValueError("Output directory must be outside the archive and object store")
    if not (archive / ".git").is_dir():
        raise ValueError(f"Archive is not a Git repository: {archive}")

    head, all_rows, object_index, checksums = read_snapshot(archive, store)
    chosen = sorted(
        (row for row in all_rows if selected_path(row["path"])),
        key=lambda row: row["path"],
    )
    if not chosen:
        raise ValueError("The requested manifest scope selected no rows")
    paths = [row["path"] for row in chosen]
    if len(paths) != len(set(paths)):
        raise ValueError("Manifest contains duplicate selected paths")

    by_hash = {}
    by_object_path = {}
    for row in chosen:
        path = safe_relative(row["path"], "manifest path")
        if row.get("storage") not in {"git", "object"}:
            raise ValueError(f"Unknown storage type for {path}")
        if row.get("storage") == "object":
            digest = row["sha256"]
            object_path = safe_relative(row["object"], "object path")
            if digest in by_hash and by_hash[digest]["object"] != object_path:
                raise ValueError(f"Conflicting object paths for {digest}")
            by_hash[digest] = row
            by_object_path[object_path] = digest

    index_by_hash = {entry["sha256"]: entry for entry in object_index}
    if len(index_by_hash) != len(object_index):
        raise ValueError("External objects index has duplicate SHA-256 entries")
    verified_index = []
    for digest, row in sorted(by_hash.items()):
        entry = index_by_hash.get(digest)
        if not entry:
            raise ValueError(f"Object absent from external index: {digest}")
        if entry.get("object") != row.get("object") or entry.get("bytes") != row.get("bytes"):
            raise ValueError(f"Manifest/index disagreement for object {digest}")
        verified_index.append(verify_object(store, row, entry, checksums))

    for row in chosen:
        if row.get("storage") == "git":
            path = safe_relative(row["path"], "Git path")
            process = subprocess.Popen(
                ["git", "-C", str(archive), "cat-file", "blob", f"{head}:{path}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            assert process.stdout is not None
            inline_hash, inline_size = digest_stream(process.stdout)
            error = process.stderr.read() if process.stderr else b""
            if process.wait():
                raise ValueError(f"Git blob unavailable for {path}: {error[:500]!r}")
            if (inline_hash, inline_size) != (row["sha256"], row["bytes"]):
                raise ValueError(f"Captured Git blob differs from manifest: {path}")

    created = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    scope = {
        "created_utc": created,
        "archive_head": head,
        "study_backup": "explicitly partial portable backup; not a full runtime backup",
        "selected_prefixes": [STUDY_PREFIX, *ADDITIONAL_PREFIXES],
        "excluded_prefixes": [STUDY_EXCLUDED_PREFIX],
        "manifest_rows": len(chosen),
        "unique_external_objects": len(verified_index),
        "contents": [
            "selected rows from the archive backup manifest",
            "selected external objects index entries",
            "only unique zstd objects referenced by selected rows",
            "inline Git files remain in the captured Git commit",
        ],
        "exclusions": [
            "runtime images and runtime-home trees",
            "model tensor weights and private runtime caches; public tokenizer metadata is retained",
            "authentication and session state",
            "all unselected sibling artifact-store objects",
        ],
    }

    out_dir.parent.mkdir(parents=True, exist_ok=True)
    # Reserve the exact requested destination atomically; never replace an
    # existing directory, even if another process creates it during the build.
    out_dir.mkdir(exist_ok=False)
    try:
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        bundle = out_dir / f"quality-object-backup-{stamp}.tar.zst"
        manifest_payload = "".join(
            json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
            for row in chosen
        ).encode()
        index_payload = (
            json.dumps(verified_index, sort_keys=True, indent=2) + "\n"
        ).encode()
        scope_payload = (json.dumps(scope, sort_keys=True, indent=2) + "\n").encode()

        with bundle.open("xb") as output:
            process = subprocess.Popen(
                ["zstd", "-q", "-T1", "-3", "-c"],
                stdin=subprocess.PIPE,
                stdout=output,
                stderr=subprocess.PIPE,
            )
            assert process.stdin is not None
            try:
                with tarfile.open(fileobj=process.stdin, mode="w|", format=tarfile.PAX_FORMAT) as tar:
                    add_bytes(tar, "manifest.jsonl", manifest_payload)
                    add_bytes(tar, "objects-index.json", index_payload)
                    add_bytes(tar, "SCOPE.json", scope_payload)
                    for entry in verified_index:
                        add_object(tar, store, entry)
            except Exception:
                process.stdin.close()
                process.kill()
                process.wait()
                raise
            process.stdin.close()
            stderr = process.stderr.read() if process.stderr else b""
            if process.wait():
                raise RuntimeError(f"zstd bundle compression failed: {stderr[:500]!r}")

        bundle_hash, bundle_size = digest_stream(bundle.open("rb"))
        build = {
            "created_utc": created,
            "bundle_file": bundle.name,
            "bundle_sha256": bundle_hash,
            "bundle_bytes": bundle_size,
            "archive_head": head,
            "manifest_rows": len(chosen),
            "unique_external_objects": len(verified_index),
            "remote_uploaded": False,
        }
        (out_dir / "BUILD.json").write_text(json.dumps(build, indent=2) + "\n")
        return out_dir / bundle.name
    except Exception:
        shutil.rmtree(out_dir, ignore_errors=True)
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", required=True, type=Path, help="New output directory")
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--store", type=Path, help="External object store (default: archive sibling)")
    return parser.parse_args()


def main() -> int:
    try:
        bundle = make_bundle(parse_args())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(bundle)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
