# Complete speaking-route alignment review

Reviewed 5 November 2026. Scope: all sixteen main AI slides and both short speaking scripts, plus all four scripted backup slides. The eighteen AI appendix pages were checked for order/title routing; four have short spoken paragraphs. The long teaching guides are study resources, not the spoken script. No new performance or quality measurement was made.

The active order is defined by `presentation.xml` relationships. Older unreferenced `slide*.xml` parts remain in this deck and must not be mistaken for audience-visible pages. The earlier 17-layout sentence was absent from the active topology page, even though obsolete embedded parts contained that number.

Script numbers remain **0–15**, as requested by the owner. Printed deck numbers remain **01–16**. Backup script 18 means printed slide 19. This is an intentional offset, not a missing slide.

## All main slides

| Script / printed page | Spoken point and visual support | Review and action |
|---|---|---|
| 0 / 01 | Two nodes, sixteen H200; 4,000 input / 200 output; first token ≤3,000 ms, mean token gap ≤20 ms, joint fraction ≥90%; qualifying throughput | Added the missing input/output lengths. Existing hardware label, three latency/eligibility columns and score formula support the rest. Errors stay in the eligibility denominator. |
| 1 / 02 | Architecture decision, scoped code contribution, controlled backend/load findings; existing libraries reused | Three columns already match. No claim of inventing NIXL, SGLang or kernel libraries. No extra slide text needed. |
| 2 / 03 | Seventeen explored layouts and GPU-budget tradeoff; observations used different loads | Added a visible orange **17 layouts explored** and the unmatched-load qualification. Existing prefill/decode columns and shared budget explain why the search exists. This is not a controlled ranking or global-optimum claim. |
| 3 / 04 | Two four-GPU prefill workers on node 0, one eight-GPU decode worker on node 1; expert distribution and KV transfer | Architecture diagram already shows both workers, eight decode chips, TP/EP labels and cross-role arrows. TP8/EP8 uses the same eight GPUs, not sixty-four. |
| 4 / 05 | Loaded workers still time out during warmup after six minutes, before any scored benchmark | Existing 360-second label and request-path diagram match. Moved source-code findings out of this spoken section and onto the following intervention slide. |
| 5 / 06 | Whole-pool metadata motivates request pages; coalesce only safely; same bytes; 720 CPU checks | Source finding now spoken here, with the matching before/after visual. Added the source-and-destination contiguity condition and partial-token spacing rule. CPU checks are not presented as a GPU speed benchmark. |
| 6 / 07 | Patched warmup and a full benchmark complete with zero scored errors | Existing before/after columns match. Transition now explicitly calls later performance experiments a separate question. Descriptor-only speedup remains unmeasured, stated on the slide and in backup 20. |
| 7 / 08 | Three profile activity groups; overlap prevents a request-time partition; phase-specific DeepGEMM trial | Reworded speech to call the picture a three-column map, not a displayed profiling chart. Added overlap qualification and the tested prefill choice: fixed decode, about +1.8% goodput, repeated improvement. No claim that a later profile predicted the earlier winner. |
| 8 / 09 | AUTO decode versus HPC-Ops, same 16 H200, concurrency 60, DeepGEMM prefill/chunk 8192 and remaining controls | Existing held-fixed box and control/candidate labels support each setup claim. Speech uses simple words and does not read long job IDs or chunk numerals. |
| 9 / 10 | HPC-Ops +5.3% versus AUTO; mean first token +125 ms, mean gap −1.6 ms; independent repeat | Existing three before/after columns and repeat caption match. Changed spoken TTFT rounding from a tenth of a second to about 125 milliseconds to point directly to the displayed +125.34 ms. This remains a recipe-level comparison, not an isolated kernel mechanism. |
| 10 / 11 | N62→N64 about +1%; repeat; N68 full run below a tenth of a percent; retain N64 | Existing three result columns support the numbers. Added the explicit 1% usefulness cutoff and a conditional throughput/wait tradeoff. No claim that N68 was measured to have worse latency. |
| 11 / 12 | Each dot is a request; x=TTFT ms, y=request-mean ITL ms; limits 3000/20; 27 orange TTFT-only misses; 98.6% pass | Checked plot labels, red boundaries, orange failure dots and count panel: 1,875/1,902, no ITL misses, no request errors. No cause is assigned to queueing, computation or transfer from this scatter alone. |
| 12 / 13 | Router readiness preceded registration; repaired full package startup/serving/reader/cleanup; about 3,052 good output tokens/s | Added the startup failure and model/live-worker wait, matching the script. Existing three-step flow and 3,051.52 score support the completed rerun. This is local portable acceptance, not organiser certification or a matched new speedup. |
| 13 / 14 | H100 ideas tested directly on H200; port about −10%, chunk refinement still −4.5%; other gains below 1% | All three existing result columns and retain-H200 decision match. Different hardware scores are not combined into a controlled comparison. |
| 14 / 15 | Lower graph-capture memory did not improve goodput; shallow speculative setting also lost | Existing sparse graph and EAGLE3 panels show the proxy and −0.37%/−2.08% outcomes. Speech correctly says capture memory, not total sampled VRAM. It rejects only the tested settings. |
| 15 / 16 | Three lessons; portable score; complete paired local quality; about 99.9% reference-score retention | Added the MMLU-Pro name and same 12,032-question coverage. Existing score, retention metric and organiser/local boundary match. Retention is not absolute accuracy or official certification. |

## All scripted backups

| Script / printed page | Check |
|---|---|
| 18 / 19 | Same 12,032 questions; 9,460 reference versus 9,452 candidate; eight fewer correct; 99.9154% retention; local gate. Existing counts and formula match the spoken approximations. |
| 19 / 20 | Whole pool versus one request, 403.8 million versus 188 ranges; CPU equivalence and GPU transport are distinct. Count comparison is not a speedup factor. Existing visual supports the spoken scope explanation. |
| 20 / 21 | 22271 timed out before scoring; patched 22294 completed warmup and full N32, zero errors; no isolated descriptor speedup. Existing evidence table matches. |
| 30 / 31 | Model registration readiness repair, complete rerun and approximately 3,052 good tokens/s. Added the 3,051.52 score to the slide's acceptance line; other reader failures are study/Q&A context, not mandatory spoken content. |

## Evidence and numerical checks

- Seventeen layout observations and feasibility limits: [retained thinking process](../teacher-qa-preparation-20261101/THINKING_PROCESS_EN.md), architecture section.
- NIXL code/CPU/GPU boundaries: [request-scoped investigation](../team-research-atlas-20261104/research-notes/ai/nixl-request-scope.md) and its original patch, geometry and warmup-log links.
- Prefill: jobs 24263/24291, followed by fresh control 24320 and repeat 24327. Initial +1.8136%; repeat +1.7401% against its fresh control. “About 1.8%, repeated improvement” is an approximation across these separate pairs, not two identical deltas.
- Decode: 24912 AUTO 2,838.853 versus 24913 HPC-Ops 2,989.175 good output tokens/s. +5.295%; mean TTFT 822.292→947.627 ms, mean ITL 16.579→14.934 ms. See retained backend records and [thinking process](../teacher-qa-preparation-20261101/THINKING_PROCESS_EN.md).
- Concurrency: +1.082867% N62→N64; independent N64 differs −0.013634%; full N68 +0.083056%, below the team’s prospective 1% usefulness cutoff.
- Scatter: 1,875/1,902 =98.580442%; 27 TTFT-only misses, zero ITL misses/errors. This is job 26766, not the separate portable run's request population.
- Portable: 28197 =3,051.518173 good output tokens/s; its own count is 1,881/1,907, distinct from scatter job 26766. See [accepted entry](../../notes/ai-final-portable-acceptance-20261102.md).
- Quality: 9,452/9,460 =99.915433% retention, measured on the same 12,032 questions per deployment. Accuracy 78.557181% versus 78.623670%. [Full quality report](../ai-quality-verification-20261103/FULL_RESULTS.md). Sixteen allocations are eight shards per role, not sixteen failed measurements.

## Delivery and preservation

English remains approximately 12–13 minutes under the stated pace/pause assumptions; no timed human rehearsal is claimed. Speak rounded values and point to the exact displayed figures. Explanatory transitions do not require duplicating every spoken word on the slide.

All changes are editable native PPTX text. Existing backgrounds, diagrams, slide order, hidden flags and all HPC package parts are preserved. The PDF is the established coordinate rendering with matching text overlays, checked visually; this is not a claimed Microsoft Office rendering. The legacy 78-slide root-level PPTX, long teaching-guide PDFs and historical submission ZIP are not silently overwritten. Use the canonical workspace deck and the new companion PDF for this speaking route.

The short scripts and local before-script copies remain local and uncaptured under the owner's earlier no-commit instruction. The deck, reproducible patch, audit, validation and provenance may be archived. The deck/large PDFs use the archive's external artifact store; a Git manifest is not itself an off-host copy of those large bytes.
