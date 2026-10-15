# Startup counters prepared 2026-10-15 20:20 UTC

`startup-sampler.py` is a local, unsubmitted diagnostic companion. It does not
change the frozen baseline or pilots04/05/06, stage assets, reserve SU or start
a GPU job. It imports only the Python standard library. Runtime on NSCC is
unverified because the existing VPN helper no longer finds a live session and
the existing SSH master timed out on a read-only query in this wake.

For a future instrumented allocation, launch one sampler per worker **inside
its compute container**, immediately before its final `exec` of SGLang. Supply
that worker shell's PID as `--root-pid` and a fresh artifact JSONL path as
`--out`; defaults are15s intervals and a1200s maximum. Keep the sampler's
`PBS_JOBID` in the container explicitly (the current cleanenv wrapper only
forwards QWEN variables). Run the identical observation policy for matched
control and candidate allocations before interpreting a difference. Any such
bundle must be frozen/validated separately; these instructions do not authorize
an additional simultaneous job or bypass queue, quality or budget gates.

The sampler checks UID and PID start time, walks children from the explicit
root's per-thread child lists, and excludes its own subtree. It reads only
stat/status/io/numa_maps for that tree. Output contains CPU ticks, thread count,
minor/major faults, RSS, I/O counters, CPU/memory affinity and aggregated NUMA
page counts; it never records command lines, environments or mapped filenames.
It refuses to overwrite prior evidence and its CLI requires a PBS allocation.

Interpretation:

- Use counter deltas only for the same PID/start-time identity. A newly seen
  process has no delta; exited children are missing, so sums undercount work.
- Divide CPU-tick deltas by clock ticks and elapsed sample time to estimate
  CPU use. Compare thread count and CPU masks against the allocated32CPUs per
  TP4 replica; do not infer actual NUMA locality from a CPU mask alone.
- Correlate major faults/read_bytes and NUMA placement with shard progress and
  `/get_server_info` startup times. mmap faults, shared page cache, readahead and
  network filesystem accounting prevent equating read_bytes with model traffic.
- RSS/NUMA pages can count shared mappings repeatedly across ranks. Do not sum
  RSS as physical node memory or interpret node page totals as per-GPU distance.
- Stable low I/O with high CPU suggests a different next investigation from
  high fault/I/O stalls, but neither proves causality. Storage/cache state and
  TP/EP topology must stay explicit. Do not flush system caches.

The real image source additionally shows that expert locality is checked in
`fused_moe_triton/layer.py:927–938` **after** the iterator hands a tensor to
`qwen3_moe.py:1125–1200`. The default mmap iterator builds dictionaries of
`get_tensor` views before the expert loader may skip a nonlocal weight.
This establishes control-flow order; it does not establish whether those
skipped tensors' data pages were read or an eightfold I/O reduction. Therefore
the851s versus99s prefill/decode load times remain confounded observations.

Local validation uses a controlled own child writing4MiB and spawning an own
grandchild; it checks descendant discovery, identity, counters and CLI refusal
outside PBS. No model imports or GPU execution are involved. Evidence is in
`inspection/wake-20261015-2020UTC/startup-sampler-validation.json`.

## Offline analysis prepared 2026-10-15 20:57 UTC

`python3 analyze-startup.py WORKER.jsonl --out FRESH-analysis.json` reads one
sampler journal without accessing processes, model files or GPUs. Run separately
for each worker. It uses monotonic sample times and metadata clock ticks to
calculate observed CPU-seconds/wall-second and I/O rates. It recomputes deltas
from raw counters for matching `(pid,start_ticks)` identities rather than trusting
embedded deltas. New/disappeared identities, missing counter coverage, resets,
read errors and gaps over1.5times the nominal interval remain explicit.
Missing coverage produces null, not zero. CPU cores do not represent a percent
of allocated CPUs. No summed RSS, storage-throughput claim or automatic
bottleneck classification is produced.

An unfinished final JSONL line is ignored and flagged for live snapshots;
malformed complete lines and nonincreasing monotonic times are rejected.
Output uses exclusive creation and retains the input SHA256. Keep the original
journal. A single sample has no rate interval and is not evidence of inactivity.

Offline validation passed PID reuse, missing I/O, counter reset, sample gap,
incomplete tail, invalid inputs and refusal to overwrite. Previously preserved
local own-child samples reproduce wchar4194309 and write_bytes0. Their analysis
has explicitly constructed local-test metadata; it is not a NSCC measurement.
Evidence: `inspection/wake-20261015-2055UTC/analyzer-validation.json`.
Sampler and analyzer remain local only; frozen04/05/06 and their priority,
queue/budget gates are unchanged. No instrumentation has run on NSCC.
