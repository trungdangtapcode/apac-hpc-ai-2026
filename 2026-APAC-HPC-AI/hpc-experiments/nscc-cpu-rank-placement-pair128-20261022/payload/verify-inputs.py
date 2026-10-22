"""Verify the unchanged accepted default-Scotch N128 source and a run copy."""
from pathlib import Path
import hashlib
import json
import sys


def processor_names(case):
    """Return processor directory names in numeric-safe lexical order."""
    return sorted(p.name for p in case.glob("processor*") if p.is_dir())


def expected_processor_names(ranks):
    return sorted("processor" + str(i) for i in range(ranks))


def verify_case(case, config, accepted):
    ready = json.loads((case / "CUT_READY.json").read_text())
    assert ready["ranks"] == 128 and ready["method"] == "scotch"
    assert ready["total_cells"] == 65334765
    for name, expected in accepted.items():
        path = case / name
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == expected, (str(path), actual, expected)
    assert processor_names(case) == expected_processor_names(128), (
        processor_names(case), expected_processor_names(128)
    )
    assert all(not (case / name).is_symlink() for name in ("system", "constant", "0.orig")), \
        "Writable case roots must not link into the accepted source"
    assert not (case / "system/controlDict").is_symlink(), "controlDict must be copied, not linked"
    for i in range(128):
        processor = case / ("processor" + str(i))
        assert not processor.is_symlink(), str(processor)
        for relative in ("0", "constant/polyMesh"):
            writable_tree = processor / relative
            assert writable_tree.is_dir() and not writable_tree.is_symlink(), str(writable_tree)
            assert not any(path.is_symlink() for path in writable_tree.rglob("*")), \
                "Writable processor fields/mesh must not link into the accepted source"
    if case == Path(config["source_case"]):
        assert config["method"] == "default_scotch"
        assert config["ranks"] == 128 and config["nodes"] == 1
        assert config["steps"] == 40
        assert config["practical_timing_gain_threshold_percent"] == 3.0
    return {
        "passed": True,
        "case": str(case),
        "ready": {"method": ready["method"], "ranks": ready["ranks"],
                  "total_cells": ready["total_cells"]},
        "accepted_file_count": len(accepted),
    }


def main():
    root = Path(__file__).resolve().parent
    config = json.loads((root / "inputs.json").read_text())
    accepted = json.loads((root / "accepted-inputs.json").read_text())["source"]
    case = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(config["source_case"])
    print(json.dumps(verify_case(case, config, accepted), indent=2))


if __name__ == "__main__":
    main()
