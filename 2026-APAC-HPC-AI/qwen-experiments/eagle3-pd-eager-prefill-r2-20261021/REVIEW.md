# Full-PD startup repaired; warmup launcher fails

Job **223053.pbs111** is F/exit **127**, with **507 seconds** allocated runtime and **288.426667 SU** estimated allocation charge. Charge posting/reconciliation remains separate. Raw and submitted payload hashes pass. [Machine inspection](REVIEW.json), [replay](review.py), [sealed collection](collection.json).

Both TP4 prefills and TP8 decode reach native readiness; the head script records prefill-0 at 444 seconds, prefill-1 at 445, decode at 446, and all workers plus router at 490 seconds. Every prefill rank shows both target/draft prefill graph-disable decisions. All 16 ranks initialize NIXL and both KV caches as BF16; decode draft decode/extend graph captures complete. Pre-cleanup worker logs contain no Traceback, RuntimeError or ERROR strings. This string inspection is bounded evidence, not proof of all runtime health.

The next step fails immediately: `timeout: failed to run command 'srun': No such file or directory`. The PBS adapter exports srun as a Bash function. Direct shell calls work, but GNU timeout executes an external command and cannot execute that function. The newly added outer timeout therefore never launches pair warmup. This is an orchestration regression introduced in this repair; startup evidence is valid, but the integration test **fails**. No actual user diagnostic IDs or equivalence result exists, and post-warmup rank/thread locality capture was not reached. Router readiness is not proof of successful heterogeneous KV transfer.

| Role | Startup samples | Distinct GPU UUIDs | Maximum sampled VRAM (MiB/device) |
|---|---:|---:|---:|
| prefill-0 | 77 | 4 | 75192.0 |
| prefill-1 | 76 | 4 | 75192.0 |
| decode-0 | 75 | 8 | 78334.0 |

The role UUID sets are disjoint, covering all 16 H100s. Server status counts, sample bounds and sampled activity are retained in REVIEW.json. These are startup samples, with no scored load, tail latency, effective concurrency or goodput result. Node CPU/RAM/network counters were collected but not converted into demand/rates. Launch masks exist; actual scheduler/rank/thread placement was not collected. No bottleneck is inferred from startup utilization. The inspection initially assumed a single server-status field and failed on the collector's HTTP-result schema; it now retains HTTP status, earlier error status or explicit missing as appropriate. No raw evidence was changed.

Next distinct repair: use child Bash inside timeout to invoke the exported shim, preserving argv, deadlines and token gates. Test actual shim CPU dry-run dispatch, nonzero status propagation and timeout termination before a separately frozen allocation. Retain this failed payload unchanged. H200/H100 throughput incumbents and the official accuracy gap remain unchanged.
