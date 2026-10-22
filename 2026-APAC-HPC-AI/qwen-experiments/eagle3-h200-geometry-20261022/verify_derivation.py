#!/usr/bin/env python3
"""Verify provenance and that the generated module contains only two edits."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from derive import DEFAULT_SOURCE, EXPECTED_SOURCE_SHA256

HERE = Path(__file__).resolve().parent
IMPORT_BLOCK = (
    "\nfrom sglang.srt.disaggregation.nixl.kv_geometry import (\n"
    "    instrument_registration as _instrument_nixl_registration,\n)\n"
)
OLD_CALL = "self.register_buffer_to_engine()"
NEW_CALL = "_instrument_nixl_registration(self, self.register_buffer_to_engine)"


def main():
    metadata = json.loads((HERE / "DERIVATION.json").read_text())
    source = Path(metadata["source_path"]).read_bytes()
    derived_path = HERE / metadata["derived_file"]
    derived = derived_path.read_bytes()
    if hashlib.sha256(source).hexdigest() != EXPECTED_SOURCE_SHA256:
        raise SystemExit("pinned source hash mismatch")
    if hashlib.sha256(derived).hexdigest() != metadata["derived_sha256"]:
        raise SystemExit("derived source hash mismatch")
    text = derived.decode("utf-8")
    if text.count(IMPORT_BLOCK) != 1 or text.count(NEW_CALL) != 1:
        raise SystemExit("expected instrumentation import/call is missing or duplicated")
    restored = text.replace(IMPORT_BLOCK, "", 1).replace(NEW_CALL, OLD_CALL, 1)
    if restored.encode("utf-8") != source:
        raise SystemExit("derived module contains changes beyond helper import and call wrapper")
    print(json.dumps({
        "passed": True,
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "derived_sha256": hashlib.sha256(derived).hexdigest(),
        "only_expected_edits": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
