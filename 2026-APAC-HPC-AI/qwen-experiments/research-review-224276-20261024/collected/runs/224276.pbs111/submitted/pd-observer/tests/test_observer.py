import json
import importlib.util
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import observer
from validate_receipts import validate
gate_spec = importlib.util.spec_from_file_location(
    "prefill_gate", Path(__file__).resolve().parents[2] / "check_prefill_observer.py")
prefill_gate = importlib.util.module_from_spec(gate_spec)
gate_spec.loader.exec_module(prefill_gate)


class FakeRow:
    def __init__(self, nbytes):
        self.nbytes = nbytes


class FakeTensor:
    def __init__(self, ptr, shape, row_bytes, dtype="torch.float16"):
        self._ptr = ptr
        self.shape = tuple(shape)
        self._row_bytes = row_bytes
        self.dtype = dtype
        self.nbytes = self.shape[0] * row_bytes

    def stride(self):
        if len(self.shape) == 2:
            return (self.shape[1], 1)
        return tuple(1 for _ in self.shape)

    def __getitem__(self, index):
        if index != 0:
            raise IndexError(index)
        return FakeRow(self._row_bytes)

    def data_ptr(self):
        return self._ptr


def install_fake_sglang(rank=0):
    dist = types.ModuleType("torch.distributed")
    dist.is_initialized = lambda: True
    torch = types.ModuleType("torch")
    torch.distributed = dist
    package = types.ModuleType("sglang")
    package.__path__ = []
    srt = types.ModuleType("sglang.srt")
    srt.__path__ = []
    distributed = types.ModuleType("sglang.srt.distributed")
    distributed.get_tp_group = lambda: types.SimpleNamespace(rank=rank)
    sys.modules.update({
        "torch": torch, "torch.distributed": dist,
        "sglang": package, "sglang.srt": srt,
        "sglang.srt.distributed": distributed,
    })


def good_receipt(role, rank, row_counts=(10, 10)):
    names = ["output_ids", "output_hidden_states"]
    rows = []
    for name, width, count in zip(names, (64, 128), row_counts):
        rows.append({"name": name, "shape": [count, width // 2], "strides": [width // 2, 1],
                     "dtype": "torch.float16", "row_nbytes": width, "item_len": width,
                     "row_count": count, "nbytes": count * width})
    return {"schema": "eagle3-pd-metadata-v1", "role": role, "role_kind": role.split("-", 1)[0], "tp_rank": rank,
            "rank_source": "initialized sglang.srt.distributed.get_tp_group().rank",
            "ordered_names": names, "rows": rows, "tensor_count": len(rows),
            "total_row_count": sum(row["row_count"] for row in rows),
            "total_bytes": sum(row["nbytes"] for row in rows),
            "ptr_list_count": len(rows), "lens_list_count": len(rows), "item_lens_list_count": len(rows),
            "original_ptrs_equal_tensor_data_ptrs": True,
            "original_lens_equal_tensor_nbytes": True,
            "original_item_lens_equal_tensor_row_nbytes": True}


class ObserverTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.old_env = {k: os.environ.get(k) for k in ("QWEN_ROLE_NAME", "QWEN_ARTDIR")}
        os.environ["QWEN_ROLE_NAME"] = "prefill-0"
        os.environ["QWEN_ARTDIR"] = self.temp.name
        install_fake_sglang()
        observer._transfer_counts.clear()
        observer._transfer_dropped.clear()

    def tearDown(self):
        for key, value in self.old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.temp.cleanup()

    def test_metadata_wrapper_preserves_exact_tuple_and_is_once(self):
        class Buffers:
            output_ids = FakeTensor(111, (3, 32), 128, "torch.int32")
            cached_tokens = FakeTensor(222, (3, 16), 64, "torch.int32")
            output_token_logprobs_val = None
            output_token_logprobs_idx = None
            output_top_logprobs_val = None
            output_top_logprobs_idx = None
            output_token_sampling_mask_len = None
            output_token_sampling_mask_idx = None
            output_token_sampling_logprobs = None
            output_topk_p = None
            output_topk_index = None
            output_hidden_states = None
            output_dsa_topk_indices = None
            bootstrap_room = None

        a, b = Buffers.output_ids, Buffers.cached_tokens
        exact = ([a.data_ptr(), b.data_ptr()], [a.nbytes, b.nbytes], [128, 64])
        method = observer.wrap_get_buf_infos(lambda self: exact)
        self.assertIs(method(Buffers()), exact)
        rec = json.loads((Path(self.temp.name) / "pd-observer/prefill-0/tp-0/metadata.json").read_text())
        self.assertEqual(rec["ordered_names"], ["output_ids", "cached_tokens"])
        self.assertEqual(rec["rows"][0]["row_nbytes"], 128)
        self.assertTrue(rec["original_ptrs_equal_tensor_data_ptrs"])
        self.assertTrue(rec["original_lens_equal_tensor_nbytes"])
        self.assertTrue(rec["original_item_lens_equal_tensor_row_nbytes"])
        self.assertNotIn("111", json.dumps(rec))
        method(Buffers())
        self.assertEqual(len(list((Path(self.temp.name) / "pd-observer/prefill-0/tp-0").glob("metadata.json"))), 1)

    def test_missing_identity_fails_closed_after_original_call(self):
        calls = []
        os.environ.pop("QWEN_ROLE_NAME")
        method = observer.wrap_get_buf_infos(lambda self: calls.append(True) or ([], [], []))
        with self.assertRaises(RuntimeError):
            method(object())
        self.assertEqual(calls, [True])

    def test_transfer_return_identity_and_exception_markers(self):
        handle = object()
        success = observer.wrap_transfer(lambda self, *a, **kw: handle, "send_kvcache_slice")
        self.assertIs(success(object(), "peer", [1, 2], [3], "tag"), handle)

        def raises(self, *args, **kwargs):
            raise LookupError("safe error")

        failure = observer.wrap_transfer(raises, "send_aux")
        with self.assertRaises(LookupError):
            failure(object(), "peer", 4, [0xBAD, 0xBAD2], 5, "tag")
        lines = [json.loads(line) for line in (Path(self.temp.name) / "pd-observer/prefill-0/tp-0/transfers.jsonl").read_text().splitlines()]
        self.assertEqual([x["marker"] for x in lines], ["start", "returned_handle", "start", "exception"])
        self.assertEqual(lines[0]["source_page_count"], 2)
        self.assertEqual(lines[2]["row_indices"], [0, 1])
        self.assertEqual(lines[2]["source_request_page_index"], 4)
        self.assertNotIn('"peer"', json.dumps(lines))
        self.assertNotIn("0xBAD", json.dumps(lines))
        self.assertTrue(all("completion" not in x or "not transfer completion" in x["completion_semantics"] for x in lines))

    def test_validator_requires_complete_geometry_and_measured_cross_role_widths(self):
        records = [good_receipt("prefill-0", i, (7, 7)) for i in range(4)]
        records += [good_receipt("prefill-1", i, (7, 7)) for i in range(4)]
        records += [good_receipt("decode-0", i, (512, 512)) for i in range(8)]
        with tempfile.TemporaryDirectory() as d:
            paths = []
            for i, record in enumerate(records):
                path = Path(d) / f"{i}.json"
                path.write_text(json.dumps(record))
                paths.append(path)
            report = validate(paths)
            self.assertTrue(report["complete"])
            self.assertEqual(report["role_rows"]["prefill-0"]["observed_row_counts"], [7])
            self.assertEqual(report["role_rows"]["decode-0"]["observed_row_counts"], [512])
            with self.assertRaisesRegex(ValueError, "incomplete decode"):
                validate(paths[:-1])
            bad = dict(records[-1])
            bad["rows"] = [dict(records[-1]["rows"][0], item_len=999), records[-1]["rows"][1]]
            bad_path = Path(d) / "bad.json"
            bad_path.write_text(json.dumps(bad))
            with self.assertRaises(ValueError):
                validate(paths[:-1] + [bad_path])
            missing = dict(records[-1])
            missing.pop("ordered_names")
            missing_path = Path(d) / "missing.json"
            missing_path.write_text(json.dumps(missing))
            with self.assertRaisesRegex(ValueError, "missing/contradictory ordered names"):
                validate(paths[:-1] + [missing_path])
            cross_paths = paths[:-8]
            for i, original in enumerate(records[-8:]):
                cross_role = json.loads(json.dumps(original))
                cross_role["rows"][0]["row_nbytes"] = 66
                cross_role["rows"][0]["item_len"] = 66
                cross_role_path = Path(d) / f"cross-role-{i}.json"
                cross_role_path.write_text(json.dumps(cross_role))
                cross_paths.append(cross_role_path)
            with self.assertRaisesRegex(ValueError, "actual per-item widths"):
                validate(cross_paths)
            contradictory = json.loads(json.dumps(records[-1]))
            contradictory["original_item_lens_equal_tensor_row_nbytes"] = False
            contradictory_path = Path(d) / "contradictory.json"
            contradictory_path.write_text(json.dumps(contradictory))
            with self.assertRaisesRegex(ValueError, "contradictory source-list"):
                validate(paths[:-1] + [contradictory_path])

    def test_transfer_limit_is_bounded(self):
        for _ in range(observer.MAX_TRANSFER_RECORDS + 4):
            observer._bounded_transfer_record("test", "peer", {"marker": "start"})
        file = Path(self.temp.name) / "pd-observer/prefill-0/tp-0/transfers.jsonl"
        self.assertEqual(len(file.read_text().splitlines()), observer.MAX_TRANSFER_RECORDS)
        self.assertEqual(observer._transfer_dropped["prefill-0:0"], 4)

    def test_prefill_gate_requires_all_four_ranks_and_loaded_source_reports(self):
        root = Path(self.temp.name)
        role = "prefill-0"
        for rank in range(4):
            directory = root / "pd-observer" / role / f"tp-{rank}"
            directory.mkdir(parents=True)
            (directory / "metadata.json").write_text(json.dumps(good_receipt(role, rank)))
        source_dir = root / "pd-observer" / "source-modules" / role
        source_dir.mkdir(parents=True)
        for short, digest in (("utils", prefill_gate.UTILS_SHA256), ("conn", prefill_gate.NIXL_SHA256)):
            module = ("sglang.srt.disaggregation.utils" if short == "utils"
                      else "sglang.srt.disaggregation.nixl.conn")
            (source_dir / f"{short}.json").write_text(json.dumps({
                "schema": "eagle3-pd-source-module-v1", "role": role,
                "module": module, "sha256": digest,
            }))
        result = prefill_gate.validate_receipts(root)
        self.assertEqual(result["rank_set"], [0, 1, 2, 3])
        (root / "pd-observer/source-modules/prefill-0/conn.json").unlink()
        with self.assertRaisesRegex(ValueError, "source reports"):
            prefill_gate.validate_receipts(root)


if __name__ == "__main__":
    unittest.main()
