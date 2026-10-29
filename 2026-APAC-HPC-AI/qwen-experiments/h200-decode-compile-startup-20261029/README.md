# Qwen decode compile startup observer

This is a candidate startup receipt/gate for the official Qwen3-235B-A22B
FP8-weights with BF16 activations model path. It does not alter model code or submit a benchmark. Native
source remains hash guarded at `77b1e38d...d33a48c`.

## Controller integration contract

The serving controller must expose this directory only to each decode Python worker
before process creation, with:

```text
PYTHONPATH=<this-directory>:$PYTHONPATH
QWEN_TORCH_COMPILE_OBSERVER=1
QWEN_TORCH_COMPILE_RECEIPT_DIR=<shared-job-filesystem>/compile-receipts
QWEN_EXPERIMENT_ID=<immutable-experiment-id>
QWEN_ROLE_NAME=decode-0
```

Python's `sitecustomize.py` first chains the image's pinned
`/etc/python3.12/sitecustomize.py`, then installs the observer in each decode worker.
It hooks the native SGLang `patch_model` context manager and PyTorch `torch.cuda.graph`
context manager. It emits no per-token or per-request logs. It creates a
receipt when a model compile context is actually observed. The source guard is
fail closed and the native files are not modified. The observer adds Python
wrapping and counter snapshot overhead; quantify that before comparing scores.

After all expected worker startup captures complete, but before AIPerf, run:

```bash
python check_compile_receipts.py "$QWEN_TORCH_COMPILE_RECEIPT_DIR" \
  --world-size 8 --job-id "$SLURM_JOB_ID" \
  --experiment-id "$QWEN_EXPERIMENT_ID" --role decode-0 \
  --json-out "$QWEN_TORCH_COMPILE_RECEIPT_DIR/gate.json"
```

The return code must be zero and `ready_for_aiperf` must be true before any
scored request is sent. A stale/missing job or experiment ID, wrong role,
uninitialized process group, duplicate rank process, missing rank, missing shape 50–54, missing capture,
wrapper without numeric compile evidence or unexpected source stops the run.
Do not disable startup warmup to make the gate pass. If the native server uses a
different graph-capture API or shape schedule, the gate should fail; review the
actual receipt and extend only after proving the interface.
The pinned backend also has a conditional memory-saver capture adapter; if the
candidate enables that branch, this observer must prove its path separately.

## Scope and limits

The successful one-H200 probe 27340 exercised a tiny synthetic BF16 module at
shapes 1, 52 and 64. All three had Dynamo graph activity, positive Inductor
kernel generation and CUDA graph replay. It is observer-interface evidence,
not Qwen compatibility evidence. This observer has not yet run in the 8-rank
HPC-Ops model. Python may log and ignore a failing `sitecustomize` import; such
a worker emits no valid receipt and the controller must refuse AIPerf. See
[REPORT.md](REPORT.md) and `provenance.json`.

## Local receipt-gate fixtures

Run `python test_check_compile_receipts.py`. The fixtures use temporary JSON
files and do not import Torch, access a GPU, or connect to Slurm.
