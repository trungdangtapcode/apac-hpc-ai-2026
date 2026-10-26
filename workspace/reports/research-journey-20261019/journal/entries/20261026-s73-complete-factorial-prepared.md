# S73 completes the prefill graph/admission factorial

Prior evidence: actual full legacy 26313 passes local gates at 2830.923547 good output tokens/s but is 7.012% below the old three-run mean. Existing full modern 26315/S70 (disabled graph/cap 64), 26317/S71 (breakable/cap 64) and 26319/S72 (breakable/native admission) have not produced results yet. Neither the old/new gap nor those pending arms proves a causal graph/admission explanation.

S73 adds the missing disabled-graph/native-admission cell. It derives from frozen S70 and removes only its explicit prefill max-running-requests 64, plus required identity/plan metadata. Raw expected workload, worker kernels/graphs, precision, transport, output and final checker bytes remain identical. Same 16 H200/two nodes/17-minute cap/no PBS SU, full N64/4000:200/seed 2026/60:120:30, joint>=90% TTFT/ITL and zero errors/cancellations, smoke>=7/8 no regression, retrieval 12/12. This is a distinct treatment, not a duplicate of a completed run or a repeat selected for a favorable number.

Compare S70/S73 for admission effect with graphs disabled, and S73/S72 for graph effect at native admission. Single-deployment/order variability remains; useful >1% paired gain with every local gate permits proposing independent confirmation, not automatic promotion. If controls fail, no substituted historical control. Official full-set accuracy stays UNKNOWN.

CPU fixture replay uses real 26083 logs with explicitly synthetic cap edits. Expected native cap is accepted, a wrong 64 cap is rejected, payload hashes/syntax/shell checks pass and the full expected workload bytes match S70. These are preparation checks, not GPU evidence. At this checkpoint no S73 receipt exists. Preserve the four remaining queued positions, admit only after a fresh cap 5 check and document its exact dependency/ID.

Sources: h200-incumbent-recovery-20261026/derive-s73.py; serving-tuning-11/s73-h200-full-pgraph-disabled-capnative/PLAN.md and PREPARATION.json; actual 26313 full review. Frozen submitted payloads remain unchanged.
