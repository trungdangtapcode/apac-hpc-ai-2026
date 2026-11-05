# Research notes

Source-linked retrospective explanations for 31 AI milestones and 18 HPC milestones. Original run records remain unchanged. Each note separates rationale, exact changes, measurements, decisions and evidence limits.

## AI

| Milestone | Platform | Date |
|---|---|---|
| [Initial split topology](ai/early-layout.md) | H200 | 2026-10-09 |
| [Heterogeneous TP8 warmup failure](ai/tp8-warmup-failure.md) | H200 | 2026-10-10 |
| [Request-scoped NIXL descriptors](ai/nixl-request-scope.md) | H200 | 2026-10-10 |
| [Equal-TP recovery and preserved losses](ai/equal-tp-recovery.md) | H200 | 2026-10-11 |
| [Usable split baseline](ai/baseline-dense.md) | H200 | 2026-10-13 |
| [Round-robin prefill routing](ai/prefill-routing.md) | H200 | 2026-10-15 |
| [FP8 KV and decode DeepGEMM losses](ai/backend-losses.md) | H200 | 2026-10-15 |
| [MNNVL plus FlashInfer interaction](ai/mnnvl-flashinfer.md) | H200 | 2026-10-15 |
| [H100 platform becomes measurable](ai/h100-commission.md) | H100 | 2026-10-15 |
| [H100 HPC-Ops decode](ai/h100-decode-ops.md) | H100 | 2026-10-18 |
| [H100 both-phase HPC-Ops](ai/h100-both-ops.md) | H100 | 2026-10-19 |
| [DeepGEMM specifically in prefill](ai/h200-prefill-deepgemm.md) | H200 | 2026-10-17 |
| [H100 prefill alternatives lose](ai/h100-prefill-branches.md) | H100 | 2026-10-19 |
| [HPC-Ops decode with DeepGEMM/chunk8192](ai/h200-chunk-backend.md) | H200 | 2026-10-19 |
| [Separate N60 repeat/control](ai/h200-repeat-controls.md) | H200 | 2026-10-19 |
| [N60 HPC-Ops interaction repeat](ai/h200-interaction-repeat.md) | H200 | 2026-10-20 |
| [H100 load/chunk frontier](ai/h100-frontier.md) | H100 | 2026-10-20 |
| [N62 to N64 matched load](ai/n64-selection.md) | H200 | 2026-10-21 |
| [Independent N64 repeat](ai/n64-repeat.md) | H200 | 2026-10-22 |
| [N64 versus N68 stop](ai/n68-stop.md) | H200 | 2026-10-22 |
| [H100 repeated frontier remains separate](ai/h100-separate-peak.md) | H100 | 2026-10-20 |
| [Tokenizer, prefill attention and EAGLE losses](ai/phase-specific-backend.md) | H200 | 2026-10-29 |
| [Native full N64 reproduction](ai/native-repeat.md) | H200 | 2026-10-27 |
| [Cold-prefill cache candidate](ai/cache-control.md) | H200 | 2026-10-29 |
| [Sparse decode graph experiment](ai/sparse-graphs.md) | H200 | 2026-10-30 |
| [Direct H100-derived recipe check on H200](ai/cross-hardware-transfer.md) | H200 | 2026-10-31 |
| [Refine transferred recipe chunk](ai/transfer-chunk-refine.md) | H200 | 2026-10-31 |
| [Phase-specific inference mode](ai/phase-mode-test.md) | H200 | 2026-10-31 |
| [Exact packaged entry failure and acceptance](ai/packaged-acceptance.md) | H200 | 2026-11-02 |
| [N16 quality pilot fails point threshold](ai/quality-pilot.md) | H200 | 2026-11-02 |
| [Complete paired local answer-quality test](ai/quality-fullset.md) | H200 | 2026-11-02 |

## HPC

| Milestone | Platform | Date |
|---|---|---|
| [Learn the actual cluster route](hpc/access.md) | Iris | 21 Oct |
| [Establish an unchanged reference](hpc/baseline.md) | NSCC | 21 Oct |
| [Test NUMA-aware decomposition](hpc/numa.md) | NSCC | 21 Oct |
| [Separate a graph proxy from runtime](hpc/graph.md) | NSCC | 21–22 Oct |
| [Sweep rank density and node count](hpc/density.md) | NSCC | 22–23 Oct |
| [Reproduce the organizer recipe](hpc/confirm.md) | NSCC | 23 Oct onward |
| [Test hierarchical axis order](hpc/order.md) | Iris | 27–28 Oct |
| [Move communicating ranks closer](hpc/place.md) | Iris | 29 Oct |
| [Isolate a supplied runtime setting](hpc/io.md) | Iris | 1 Nov |
| [Port teammate settings fairly](hpc/team.md) | Iris | 1–2 Nov |
| [Compare our partition with Scotch](hpc/zyx.md) | Iris | 2 Nov |
| [Check a new axis order and reverse it](hpc/xzy.md) | Iris | 2 Nov |
| [Revisit native xyz with a control](hpc/xyz.md) | Iris | 3 Nov |
| [Test preparation memory policy](hpc/prep.md) | Iris | 3 Nov |
| [Check whether the preparation-policy gain repeats](hpc/native.md) | Iris | 5 Nov review (Vietnam) |
| [Test solver-rank interleave policy](hpc/rank_policy.md) | Iris | 5 Nov |
| [Qualify tiny Allreduce before a solver trial](hpc/allreduce.md) | Iris | 5 Nov review (Vietnam) |
| [Test 48-rank Scotch at a matched horizon](hpc/rank_density.md) | Iris | 5 Nov review (Vietnam) |

