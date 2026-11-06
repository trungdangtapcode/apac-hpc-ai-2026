#!/usr/bin/env python3
"""Hash the immutable initialized case once and verify isolated arm clones."""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import stat
import sys


FIELDS = ("U", "p", "k", "omega", "nut", "nuTilda")
ALLOWED_SYMLINK = "/global/exafs/groups/rdmaworkshop/2026hpcai-openfoam/occDrivAer/polyMesh"


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def rank_count(root: pathlib.Path) -> int:
    ready = (root / "READY").read_text()
    import re
    match = re.search(r"(?m)^N=(40|48)$", ready)
    if not match:
        raise ValueError("READY must identify exactly N=40 or N=48")
    return int(match.group(1))


def inventory(root: pathlib.Path) -> dict:
    rank_count_expected = rank_count(root)
    rows = {"files": {}, "symlinks": {}}
    roots = [root / "system", root / "constant"] + [root / f"processor{i}" / name for i in range(rank_count_expected) for name in ("0", "constant")]
    for top in roots:
        if not top.exists() and not top.is_symlink():
            raise ValueError(f"required source tree missing: {top}")
        if top.is_symlink():
            rows["symlinks"][top.relative_to(root).as_posix()] = os.readlink(top)
            continue
        for base, dirs, files in os.walk(top, followlinks=False):
            here = pathlib.Path(base)
            for name in list(dirs):
                path = here / name
                if path.is_symlink():
                    rows["symlinks"][path.relative_to(root).as_posix()] = os.readlink(path)
                    dirs.remove(name)
            for name in files:
                path = here / name
                rel = path.relative_to(root).as_posix()
                if path.is_symlink():
                    rows["symlinks"][rel] = os.readlink(path)
                elif stat.S_ISREG(path.lstat().st_mode):
                    rows["files"][rel] = sha256(path)
    if any(name != "constant/polyMesh" or target != ALLOWED_SYMLINK for name, target in rows["symlinks"].items()):
        raise ValueError("source contains an unapproved symlink")
    for rank in range(rank_count_expected):
        for field in FIELDS:
            if f"processor{rank}/0/{field}" not in rows["files"]:
                raise ValueError(f"missing regular initialized field: processor{rank}/0/{field}")
        times = sorted(p.name for p in (root / f"processor{rank}").iterdir()
                       if p.is_dir() and p.name.replace(".", "", 1).isdigit())
        if times != ["0"]:
            raise ValueError(f"processor{rank} must contain only initialized time 0; found {times}")
    if len(rows["files"]) < 400:
        raise ValueError(f"unexpectedly small source inventory: {len(rows['files'])} files")
    return rows


def verify_copy(source: pathlib.Path, dest: pathlib.Path, frozen_path: pathlib.Path, output: pathlib.Path) -> None:
    frozen = json.loads(frozen_path.read_text())
    copied = inventory(dest)
    if copied != frozen:
        raise ValueError("clone file hashes/symlinks differ from the frozen initialized source")
    source_inodes = {(p.stat().st_dev, p.stat().st_ino) for rel in frozen["files"] for p in [source / rel]}
    for rel in frozen["files"]:
        statrow = (dest / rel).stat()
        if (statrow.st_dev, statrow.st_ino) in source_inodes:
            raise ValueError(f"clone reuses source inode: {rel}")
    output.write_text(json.dumps({"passed": True, "regular_files": len(copied["files"]),
                                  "symlinks": copied["symlinks"], "no_source_inodes_reused": True,
                                  "manifest": copied},
                                 indent=2, sort_keys=True) + "\n")


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit("usage: seal_tree.py inventory ROOT OUTPUT | verify-copy SOURCE DEST FROZEN OUTPUT | compare ROOT FROZEN OUTPUT")
    mode = sys.argv[1]
    if mode == "inventory" and len(sys.argv) == 4:
        rows = inventory(pathlib.Path(sys.argv[2]))
        pathlib.Path(sys.argv[3]).write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n")
        print(json.dumps({"passed": True, "regular_files": len(rows["files"]), "symlinks": len(rows["symlinks"])}))
    elif mode == "compare" and len(sys.argv) == 5:
        actual = inventory(pathlib.Path(sys.argv[2]))
        expected = json.loads(pathlib.Path(sys.argv[3]).read_text())
        if actual != expected:
            raise ValueError("immutable source tree changed during the measurement")
        pathlib.Path(sys.argv[4]).write_text(json.dumps({"passed": True, "regular_files": len(actual["files"]),
                                                        "manifest": actual}, indent=2, sort_keys=True) + "\n")
    elif mode == "verify-copy" and len(sys.argv) == 6:
        verify_copy(*map(pathlib.Path, sys.argv[2:]))
        print(json.dumps({"passed": True, "copy_matches_frozen_source": True, "source_inodes_reused": False}))
    else:
        raise SystemExit("invalid seal_tree.py arguments")


if __name__ == "__main__":
    main()
