# Bounded H100 startup-cost experiment

The main serving strategy stays unchanged: the official FP8 model, plain prefill/decode disaggregation, BF16 KV, NIXL, two TP4/EP1 prefill replicas, one TP8/EP8 decode replica, HPC-Ops, chunk 4096 and round-robin. Recent full-model interventions lost: power-of-two routing -4.865%, chunk 8192 -0.7814%, chunk 2048 -26.1328%. H200 synthetic TP8 provider alternatives do not offer a consistent useful gain. Preserve those losses and stop extending those unchanged grids.

## Question and evidence

Can reading the 24 model shards once on each allocated node reduce total startup time and allocated SU, including the read itself? The pinned October ASPIRE notes report a large loading improvement after a host page-cache read. This is a cost hypothesis, not a prediction of higher good output tokens/s. Our existing weight-loader-prefetch-checkpoints flag is a different per-loader operation. The current topology has no explicit once-per-node read stage.

Metadata-only validation over existing SSH finds the model index and 24 safe single-component safetensors names totalling 236426193880 bytes. No model data was read on the login node. Actual bulk reads run only inside the allocated two-node job. The same model stays in place; no weights are copied or modified.

## Exact intervention

Both fresh derived jobs add the same common bounded helper and two-node startup stage before any model worker. The control uses mode off, reading only index/size metadata; the candidate uses mode read, consuming each shard once. Both wait for the per-node stage before launching their identical workers. Each stage uses no GPU, eight CPU I/O threads, at most 16 MiB per thread, an internal 120-second read budget and an outer 150-second timeout with a ten-second termination allowance. Paths, manifest range (200–300 GiB total), shard count and read-byte counts are checked. JSON receipts preserve index/helper hashes, logical bytes read, elapsed monotonic time, node name and node cache/memory snapshots.

Worker, model, precision, topology placement, native graph/routing guards, N54 scoring and short/long output checks are byte-identical to accepted 222382. The benchmark remains full 60-second warmup, 120-second measured window and 30-second grace at fixed 4000/200, seed 2026 and cache-busted prefixes. Hardware/server sampling and separate post-score CPU/GPU diagnostics remain matched. Both jobs use the same reduced 30-minute allocation bound; recent accepted jobs finished in roughly 12–15 minutes. No frozen prior payload, image or source guard is edited.

## What counts as a useful result

Review full local gates and all usual tails/errors, runtime/transport logs, scored queues/batches/KV, hardware/node samples and separate traces. Also require two completed node-prefetch receipts with correct modes and matching index/total sizes. Parse actual scheduler-declared stdout and worker logs for per-stage and worker readiness timing. Include all prefetch time in job-to-ready, allocated walltime and SU; do not subtract it to manufacture an improvement. Distinguish startup cost from the unchanged scored goodput interval.

One pair is descriptive. The filesystem and host page caches are not flushed, initial residency is unmeasured, allocation nodes may differ and control-first order can warm later runs. Logical bytes read do not prove cold physical storage reads; MemAvailable and Cached do not certify all shard pages are resident. A useful repeatable reduction needs a balanced independent comparison with reported node/cache state; do not automatically repeat or claim causality from one favourable pair. Keep prefetch only if the full end-to-end cost is lower without a material scored-quality/latency regression. Otherwise close this exact approach. Official full-set model accuracy remains unverified.

## Budget and queue

Two serial PBS jobs, each 16 H100 GPUs and at most 30 minutes, maximum 1024 SU each / 2048 SU total. Published Used 40272.495 SU and Balance 23727.505 SU, In Doubt zero, with the previous chunk pair charges reconciled. This leaves conservative internal headroom 8679.505 SU under the unchanged 51000 SU cap and 13000 SU project buffer. Refresh the own queue and credit under the existing budget lock before reserving and qsub; require an empty own queue for this pair, then chain candidate afterany control. Maximum three active PBS jobs and one running allocation; never retry uncertain qsub. Preserve four pending H200 model positions; no H200 speculative duplicate is added to fill the fifth slot.

## Reproduction and provenance

Read pilots.json, validation.json, prefetch-validation.json, launch-fixtures.json and frozen SHA256SUMS. The bounded CPU fixtures exercise real read bytes and reject oversized models, escaping paths and excess threads; the actual PBS shim dry run checks both zero-GPU launch mappings. These fixtures do not establish GPU performance. Collect terminal jobs with nscc-pbs/collect-run.py, then review-pbs.py and the retained inspectors. The exact upstream source is pinned in upstream-review-20261020, especially the ASPIRE notes at 3d050964d1008b97fb6d0d7ec5160087cd6883d9. Keep native Enroot/image migration a separate future reproducibility experiment; it is not combined with this test.

## Timing reader distinction

The future review-startup.py requires full serving gates and two sealed matching-mode node receipts before accepting a cost observation. It reads the actual scheduler-declared stdout. Its ALL_WORKERS_READY counter is elapsed topology-script time, not the entire allocation-to-ready interval: earlier PBS prologue is excluded. Report that counter accurately alongside complete allocated walltime/SU, rather than inventing uncollected prologue timing. Initial cache residency remains unmeasured.
