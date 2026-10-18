# Output transport diagnostic

Updated UTC: 2026-10-18T19:23:37.796712+00:00

Job 23146: COMPLETED. Recorded 132/132 responses; 120 satisfy their expected answers; 0 request errors.

The job uses unmodified monolithic TP4/EP1 and TP8/EP8 instances of the same FP8 checkpoint, with no NIXL KV transfer. It is not a ranked contest P/D benchmark or the organiser accuracy gate.

Reason: job 23128 passed the performance gate (1977.08 good tokens/s, 97.14% SLA), but only 7/8 hand-written output checks. The reverse case returned `.retsulc GNITSOER` instead of `retsulc`. The original output remains a failure; it has not been normalized into a pass.

Identical eight short questions run twice sequentially and twice at concurrency four on each of three endpoints. Twelve additional long-context retrieval prompts check independent labels on each endpoint. Actual prompt token counts and all API responses are retained. Differences alone cannot identify NIXL as the cause: batching and numerical differences must also be considered.

- [Frozen deployment](s2-output-monolithic/config.json)
- [Recorded job](output-diagnostic-job.json)
- [CPU validation](output-diagnostic-cpu-validation.json)
- [Raw responses](../runs/23146/output-diagnostic.jsonl)
- [Summary](../runs/23146/output-diagnostic-summary.json)

Completed finding: all twelve reverse-string attempts fail even without NIXL, across both TP layouts and both concurrency settings. The other 120 responses pass, including all 36 long-context retrieval checks. This shows the observed failure is not exclusive to NIXL; it does not prove the patched deployment is correct on all prompts.

Research continuation uses a separate baseline comparison: all eight original cases must be recorded, with no transport error or newly failed case versus this independent baseline. The original score stays 7/8; this is not the organiser 99% accuracy gate.
