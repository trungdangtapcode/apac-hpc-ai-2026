# Native startup passes; real PD transfer fails

Job **223055.pbs111** is **F/exit1**, **734 seconds**, estimated allocated cost **417.564444 SU**. [Sealed collection](collection.json), [runtime inspection](REVIEW.json), [replay](review.py). Raw evidence and payload hashes pass. This is a failed integration with **zero completed diagnostic responses**, not an accepted performance measurement.

Both TP4 prefills and TP8 decode initialize native BF16 target/draft KV and all 16 NIXL ranks; decode graph captures complete. Workers become ready at 543/544/545 seconds; workers plus router at 587 seconds. The repaired Bash dispatch launches the actual pair client. Its compute-task log then reports HTTP500 from **NIXL_ERR_REMOTE_DISCONNECT** at 22:46:40–41 cluster time (14:46:40–41 UTC). Both pair routers record failure. Later requests report missing remote-agent metadata and NIXL_ERR_NOT_FOUND. The chronology does not establish that missing metadata caused the first disconnect; investigate the earlier transport failure first.

The head nevertheless prints ALL_PAIRS_WARM at 659 seconds. The warmup task traceback is preserved in task-aux-node0.qXGJVGTB.log; the outer pair-warmup.log is empty. This demonstrates that the current PBS launch chain can hide a remote task's failure status. Six local mocked launcher fixtures proved local dispatch/status/timeout behavior, not real remote status propagation. A future derived bundle needs an independent explicit per-pair semantic receipt before the head can claim warmup success. Do not trust that marker or loosen the token check.

Actual rank/GPU/thread locality capture completes for all roles at 661 seconds, without affinity change; it is mapping evidence, not CPU saturation. The actual-token client starts but fails its first draft-a request with HTTP500, retaining zero response rows. The final independent check rejects it, so the failed warmup is not promoted. No 1600-ID comparison or speculative acceptance result exists.

| Role | Diagnostic samples | Distinct GPU UUIDs | Maximum sampled VRAM (MiB/device) |
|---|---:|---:|---:|
| prefill-0 | 123 | 4 | 75214.0 |
| prefill-1 | 122 | 4 | 75214.0 |
| decode-0 | 121 | 8 | 78334.0 |

All 16 device UUIDs are covered in disjoint role sets. HTTP status counts, early unavailable endpoints, sample bounds and activity are in REVIEW.json. These samples cover startup and failed diagnostic work, not scored load. CPU/RAM/network counters are retained but not converted into per-role demand/rates. No tail latency, scored batch/concurrency, goodput or bottleneck is inferred from sampled activity. Inspect the initial transfer with source/cheap transport evidence before another full model allocation.

Fresh locked AI ledger at 2026-10-21T14:51:36.290020+00:00: Used **45922.128 SU**, Balance **17053.872 SU**, In Doubt **1024.000 SU**. The uniquely posted **288.427-SU** delta reconciles parent 223053; keep the **1024-SU** maximum for 223055 until its charge posts uniquely. Conservative internal headroom is **4053.872 SU** under unchanged 51000 cap / 13000 reserve. Balance already excludes In Doubt. No new GPU job/reservation or HPC CPU action in this review.

Next: preserve the failed run; add semantic warmup proof in a new derived payload, investigate initial NIXL disconnect, and prefer a cheap supported transport gate over another blind full-Qwen run. H100/H200 throughput incumbents and official accuracy status remain unchanged.
