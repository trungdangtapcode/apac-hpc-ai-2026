#!/usr/bin/env python3
"""Verify source pins and optionally copy the reviewed draft without overwrite."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
PAYLOAD = ROOT / "mutable-proposal" / "payload"
PROVENANCE = PAYLOAD / "SOURCE_PROVENANCE.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    provenance = json.loads(PROVENANCE.read_text())
    for key, row in provenance["sources"].items():
        path = Path(row["path"])
        if not path.is_file() or sha(path) != row["sha256"]:
            raise ValueError(f"source changed since draft preparation: {key}")
    native = Path(provenance["sources"]["s30/job.sbatch"]["path"]).parent
    subprocess.run(["sha256sum", "--check", "SHA256SUMS"], cwd=native, check=True, capture_output=True)
    expected_corpus = provenance["frozen_corpus_sha256"]
    if sha(PAYLOAD / "prepared-corpus.json") != expected_corpus:
        raise ValueError("frozen prepared-corpus.json changed")
    subprocess.run(["sha256sum", "--check", "SOURCE_SHA256SUMS"], cwd=PAYLOAD, check=True)
    if (PAYLOAD / "SHA256SUMS").exists():
        raise ValueError("stale SHA256SUMS name remains in proposal")
    return provenance


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--install-to", type=Path, help="copy verified draft to a new directory; existing paths are refused")
    args = ap.parse_args()
    provenance = verify()
    if args.install_to:
        target = args.install_to.resolve()
        if target.exists():
            raise FileExistsError(f"refusing to overwrite {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(PAYLOAD, target)
        subprocess.run(["sha256sum", "--check", "SOURCE_SHA256SUMS"], cwd=target, check=True)
    print(json.dumps({"verified": True, "payload_files": len(list(PAYLOAD.iterdir())),
                      "corpus_sha256": provenance["frozen_corpus_sha256"],
                      "installed_to": str(args.install_to.resolve()) if args.install_to else None}, sort_keys=True))


if __name__ == "__main__":
    main()
