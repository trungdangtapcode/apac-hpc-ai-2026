"""CPU schema checks only; they are not a runtime or GPU readiness proof."""

import importlib.util
import json
import tempfile
from pathlib import Path

O = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("prefill_gate", O / "check_prefill_observer.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def receipt(rank, width=64):
    rows = [{"name": "output_ids", "shape": [7, width // 4], "strides": [width // 4, 1],
             "dtype": "torch.int32", "row_nbytes": width, "item_len": width,
             "row_count": 7, "nbytes": 7 * width}]
    return {"schema": "eagle3-pd-metadata-v1", "role": "prefill-0", "tp_rank": rank,
            "rank_source": "initialized sglang.srt.distributed.get_tp_group().rank",
            "ordered_names": ["output_ids"], "tensor_count": 1, "ptr_list_count": 1,
            "lens_list_count": 1, "item_lens_list_count": 1,
            "total_row_count": 7, "total_bytes": 7 * width,
            "original_ptrs_equal_tensor_data_ptrs": True,
            "original_lens_equal_tensor_nbytes": True,
            "original_item_lens_equal_tensor_row_nbytes": True,
            "rows": rows}


def write_reports(root):
    out = root / "source-modules/prefill-0"
    out.mkdir(parents=True, exist_ok=True)
    for short, module, digest in (
        ("utils", "sglang.srt.disaggregation.utils", gate.UTILS_SHA256),
        ("conn", "sglang.srt.disaggregation.nixl.conn", gate.NIXL_SHA256),
    ):
        (out / f"{short}.json").write_text(json.dumps({
            "schema": "eagle3-pd-source-module-v1", "role": "prefill-0",
            "module": module, "sha256": digest,
        }))


with tempfile.TemporaryDirectory(prefix="observer-prefill-schema-") as temporary:
    root = Path(temporary) / "pd-observer"
    for rank in range(4):
        directory = root / "prefill-0" / f"tp-{rank}"
        directory.mkdir(parents=True)
        (directory / "metadata.json").write_text(json.dumps(receipt(rank)))
    write_reports(root)
    result = gate.validate_receipts(Path(temporary))
    assert result["passed"] and result["rank_set"] == [0, 1, 2, 3]
    good = [root / "prefill-0" / f"tp-{rank}" / "metadata.json" for rank in range(4)]
    (root / "prefill-0" / "tp-3" / "metadata.json").unlink()
    try:
        gate.validate_receipts(Path(temporary))
    except ValueError:
        pass
    else:
        raise AssertionError("missing rank was accepted")
    (root / "prefill-0" / "tp-3").mkdir(exist_ok=True)
    (root / "prefill-0" / "tp-3" / "metadata.json").write_text(json.dumps(receipt(3, width=128)))
    try:
        gate.validate_receipts(Path(temporary))
    except ValueError:
        pass
    else:
        raise AssertionError("contradictory cross-rank width was accepted")

print("Prefill four-rank observer schema CPU fixtures PASS (not GPU runtime evidence)")
