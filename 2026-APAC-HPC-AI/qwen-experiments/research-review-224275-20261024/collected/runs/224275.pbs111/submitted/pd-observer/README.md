# Prospective EAGLE3 P/D observer

This CPU-tested observer is prepared for a future full H100 EAGLE3 correctness bundle. It is not installed into or applied to any frozen job. The root worker owns later bundle packaging, review, submission, and the pre-warmup gate.

## Captured evidence

The `MetadataBuffers.get_buf_infos()` wrapper calls the original method first, observes its returned three-list tuple and the matching source tensors, writes at most one `metadata.json` per worker TP rank, and returns the exact original tuple object. It records ordered tensor names, shapes, strides, dtypes, tensor and row byte widths, item lengths, row counts, list counts, total bytes, and equality checks against the original lists. Pointer values are compared in memory and never serialized.

Role identity comes from the existing `QWEN_ROLE_NAME` worker label (`prefill-0`, `prefill-1`, or `decode-0`). TP rank comes from the initialized `sglang.srt.distributed.get_tp_group().rank`, after checking that `torch.distributed` is initialized. Missing or unknown identity raises before an observer receipt is accepted.

The NIXL observer records `start` followed by `returned_handle` or `exception` for calls to `send_kvcache_slice` and `send_aux`. It stores only the SHA-256 of the peer name, row indices/counts and request page counts/indices, outcome type, and timestamps. A returned handle is explicitly not reported as transfer completion. At most 128 transfer marker records are written per process; later events are dropped. The observer does not alter transport behavior or claim that it fixes the prior disconnect.

Files are written below `$QWEN_ARTDIR/pd-observer/<QWEN_ROLE_NAME>/tp-<rank>/`. They contain no raw pointers, tensors, request text, notification strings, or peer names.

## Installation and correctness gate

Add this directory to `PYTHONPATH` for the candidate server processes after worker preflights so Python loads `sitecustomize.py`. It wraps the pinned SGLang modules after import, verifies the actual loaded `utils.py` and patched NIXL module SHA-256 values, and writes per-role source reports under `pd-observer/source-modules/`. The full derived source modules are retained under `source/` for review; the wrappers are also independently represented by `observer.py` and the import hook. Do not copy these changes into a frozen payload.

The full P/D correctness bundle uses the strict 16-receipt validator before pair warmup:

```sh
python3 /path/to/eagle3-pd-observer-20261023/validate_receipts.py "$QWEN_ARTDIR/pd-observer"
```

The command exits nonzero unless it finds exactly 16 receipts for the two four-rank prefill workers and the eight-rank decode worker. It checks all ranks, names and actual per-item widths across roles, and the recorded equality checks. It permits row counts to differ between roles and reports measured counts; it does not assume a 512-row decode pool. No pair warmup should start without a successful validation result. The separate four-rank readiness probe uses its own explicit `check_prefill_observer.py` validator for `prefill-0=4`; it does not weaken or replace this strict full-P/D validator.

## CPU checks

```sh
python3 -m unittest discover -s /path/to/eagle3-pd-observer-20261023/tests -v
```

The fake-tensor tests verify tuple identity, one receipt per rank, fail-closed identity, bounded records, transfer return/exception markers, privacy exclusions, complete 2×TP4 + TP8 validation, measured row counts, and malformed or incomplete receipt rejection. They exercise no GPU, model, scheduler, network, or transport.

## Source provenance and limits

`SOURCE_PROVENANCE.json` pins the existing image and source inputs. The full base module used for the derived NIXL module is retained with its exact input hash. This observer has no runtime evidence yet: no H100 metadata receipt, transfer event, correctness result, latency result, or score has been collected. CPU validation proves observer logic only. Method return handles do not reveal asynchronous transfer completion.
