# AI journal to presentation coverage

Updated 30 October 2026. This is an honest content audit, not a claim that every journal paragraph is visible in the deck. The shared journal also contains independent HPC records and routine submission/access records. A plan, receipt, correction and result for one hypothesis are grouped into one scientific arc.

## Audit conclusion

The previous 32 AI slides covered the architecture and result spine, but compressed several hypothesis/diagnosis/decision sequences. This update makes the transport recovery, reversed startup test, failed EAGLE progression, source-guided small trials, regime-recovery controls and real deployment corrections explicit. The talk remains 32 AI slides plus the unchanged eight HPC slides.

“Direct” means the scientific turn is visible on the named slides. “Condensed” means the visible narrative and notes summarize a broader branch; it is not every trial. “Outside visible narrative” identifies material retained in the journal/tutorial/report rather than presented as a scientific achievement. No unsupported completeness percentage is reported.

## All 32 stages in the initial retrospective

The retrospective was assembled from retained written records through 19 October; it is not a verbatim reconstruction of every past conversation.

| Stage | Research turn | Slides | Coverage | What is explained |
|---|---|---|---|---|
| 1 | Establish the rules and the actual objective | 3 | Direct | Official objective and per-request gates |
| 2 | Learn login nodes, GPU allocations and persistent storage | 4, 31 | Condensed | Platform/launcher explanation; routine shell learning stays in tutorial |
| 3 | Make the first 07/09 comparisons measurable | 6 | Direct | 07/09 measured comparison |
| 4 | Expand the topology search and correct the stopping condition | 6, 8 | Direct | 14 measured originals plus three EP2 replacements; failures retained |
| 5 | Separate incompatible FP8 layouts, startup errors and transfer timeouts | 7, 8 | Direct | Separate block incompatibility, startup and transport |
| 6 | Replace full-pool heterogeneous-TP descriptors with request-scoped work | 7 | Direct | Whole pool to request-scoped transfer with geometry checks |
| 7 | Complete the equal-TP recovery without hiding the failed attempts | 7, 22 | Condensed | Real transfer and response gates; repaired paths are not automatically selected |
| 8 | Choose a usable baseline and inspect its decode batch shapes | 5, 15, 27 | Direct | Selected roles and observed decode operating range |
| 9 | Test dense decode graphs, chunk size and standalone controls | 28, 30 | Direct | Capture/padding and chunk experiments |
| 10 | Keep a model-output baseline separate from throughput | 22 | Direct | Local output baseline versus official accuracy |
| 11 | Find a useful load range rather than increasing concurrency blindly | 12, 21 | Direct | Load range and short-to-full stopping decision |
| 12 | Change prefill routing after observing poor first-token latency | 5, 11; speaker context | Condensed | Round-robin admission motivation; historical pilot is not a current isolated gain |
| 13 | Revisit backend effects on the new, fuller pipeline | 11, 14 | Direct | Backend effects depend on pipeline and operating point |
| 14 | Follow the profile into collective and attention implementations | 13, 17, 26 | Direct | Profile-driven collective and attention questions |
| 15 | Test attention-DP as a package, without copying competitor claims | 26 | Direct | DP-attention package changes several factors; no competitor-result inference |
| 16 | Test interactions rather than adding independent speedups | 11, 14 | Direct | Interactions and independent repeats |
| 17 | Commission the second platform before comparing performance | 4, 16, 19, 20 | Direct | Commission and compare platforms separately |
| 18 | Reduce wasted startup and charge credit conservatively | 18 | Direct | Startup question, reversed pair and failed cost gate |
| 19 | Establish each platform's frontier and retain design-only alternatives | 2, 16, 26; notes | Condensed | Observed frontier separated from design/source-only alternatives |
| 20 | Test DeepGEMM specifically in prefill | 10, 14, 26 | Direct | Phase-specific DeepGEMM, with representative-kernel detours qualified |
| 21 | Locate the failed requests before choosing a latency fix | 15, 28; notes | Direct | Raw first-cohort TTFT evidence remains in score |
| 22 | Reject graph removal and correct the kernel classifier | 13, 25, 28; notes | Condensed | Graph choices and kernel-classifier corrections; kernel sums are not wall time |
| 23 | Find a useful HPC-Ops decode path on H100 | 16, 26; notes | Condensed | H100 HPC-Ops decode path has a separate platform series |
| 24 | Test prefill HPC-Ops independently and refine its load | 16, 26; notes | Condensed | H100 prefill/chunk path and negative followups; no pooled hardware score |
| 25 | Revisit chunk size on the new H200 prefill runner | 30 | Direct | Larger H200 prefill chunks lose in the retained pair |
| 26 | Reject a superficially running topology on output evidence | 7, 22; notes | Direct | Quarantine superficially running equal-TP path on SLA/output evidence |
| 27 | Find the larger H200 runner/chunk interaction | 10, 14 | Direct | H200 runner/chunk interaction |
| 28 | Repeat the exact configuration, not merely another high score | 12, 14, 25 | Direct | Exact configuration and protocol replication |
| 29 | Close tested prefill branches that did not improve H100 | 17, 26; notes | Condensed | H100 prefill/collective/attention branches close at tested settings |
| 30 | Fix two review mistakes without changing the raw experiments | 13, 26, 31; notes | Direct | Correct reviewer and symbol-based interpretations without rewriting raw runs |
| 31 | Collect CPU evidence and isolate the next phase hypothesis | 18, 26; notes | Condensed | CPU/static locality and phase hypotheses are leads, not CPU-bottleneck proof |
| 32 | Preserve the reasoning as well as the measurements | 9; this coverage record | Outside visible narrative | Full reasoning and provenance live in journal, report and source index |

## Later research arcs

| Arc | Slides | Reasoning retained |
|---|---|---|
| N62/N64 replication and N68 short/full reversal | 12, 25 | Question → prospective full test → repeat → reject a short-only apparent gain |
| EAGLE dtype/KV/transport and role-aware validator recovery | 7, 22, 23 | Failed placement → validator defect → corrected short trial → full shallow loss |
| Modern-regime recovery and graph/admission controls | 25 | Observed drift → resolved-argument inspection → isolated controls → unresolved causal variation |
| Source-supported tokenizer and prefill collective choices | 21 | Exact-ID preflight and actual native dispatch → full paired points → no useful gain |
| Portable replay namespace and canonical alias corrections | 31 | Static pass → real client success but failed postprocessing → second defect → compute verification |
| Sparse capture tradeoff, model compile and C++ prerequisite | 26, 28; notes | Activation/build proof remains separate from model correctness and goodput |

## Supporting entry index

The following index routes source entries to a research family. Routing uses titles/filenames to make navigation reviewable; it is not semantic certification that each entry is completely narrated. The curated stage/arc tables above define the assessed presentation coverage. Administrative records and the independent HPC track are explicitly distinguished.

### Measurement, profiling and quality

- H100 equal-budget CPU envelope hypothesis (source journal; retained in research archive) — slides 3, 9, 13, 15, 22, 29.
- Native DeepGEMM SM-budget screen (source journal; retained in research archive) — slides 3, 9, 13, 15, 22, 29.
- 20 October 2026: inspect beyond the ranked score (source journal; retained in research archive) — slides 3, 9, 13, 15, 22, 29.
- Observer results, hardware samples and continued H200 research (source journal; retained in research archive) — slides 13, 26.
- Static CPU/GPU locality discovery before a binding experiment (source journal; retained in research archive) — slides 3, 9, 13, 15, 22, 29.
- Full-serving worker locality baseline prepared — 2026-10-20T15:07:00.574236+00:00 (source journal; retained in research archive) — slides 3, 9, 13, 15, 22, 29.
- CPU-envelope result and next component gate — 2026-10-21T03:24:42.830408+00:00 (source journal; retained in research archive) — slides 3, 9, 13, 15, 22, 29.
- 22 October: close the H200 model/image identity gap (source journal; retained in research archive) — slides 22, 27.
- 22 October: native H200 reference draft and production-interface correction (source journal; retained in research archive) — slides 3, 9, 13, 15, 22, 29.
- 22 October: freeze an asset-bound H200 exact reference (source journal; retained in research archive) — slides 3, 9, 13, 15, 22, 29.
- 22 October: native H200 reference receipt 25495 (source journal; retained in research archive) — slides 3, 9, 13, 15, 22, 29.
- 23 October: the repaired H200 exact-token reference is real and accepted (source journal; retained in research archive) — slides 3, 9, 13, 15, 22, 29.
- 23 October: submit the supported H200 reference launcher repair (source journal; retained in research archive) — slides 3, 9, 13, 15, 22, 29.
- Qualify the observer in an actual H100 server before another full model run (source journal; retained in research archive) — slides 13, 26.
- Correct the interpretation of startup-inclusive GPU averages (source journal; retained in research archive) — slides 13, 16.
### Source/library feasibility

- DeepInfer assessment and two evidence-gated research leads (source journal; retained in research archive) — slides 26.
- Upstream Qwen update review — 20 October 2026 (source journal; retained in research archive) — slides 3, 26.
### EAGLE and draft integration

- Qwen EAGLE3 header, draft metadata and native pointer checks — 2026-10-20T15:20:42.831146+00:00 (source journal; retained in research archive) — slides 7, 22, 23.
- EAGLE3 exact-token observation route — 20 October 2026 (source journal; retained in research archive) — slides 7, 22, 23.
- Small allocated EAGLE3 component gate — 2026-10-21T03:32:47.139280+00:00 (source journal; retained in research archive) — slides 7, 22, 23.
- EAGLE3 screen: match declared and initialized capacity — 21 October 2026 (source journal; retained in research archive) — slides 7, 22, 23.
- 22 October: preserve the native H200 EAGLE3 route (source journal; retained in research archive) — slides 7, 22, 23.
- 22 October: fresh draft identity before native H200 speculative integration (source journal; retained in research archive) — slides 7, 22, 23.
- H100 exit-boundary diagnostic 224155 running (source journal; retained in research archive) — slides 7, 22, 23.
- Observe the exit boundary before another full serving repair (source journal; retained in research archive) — slides 7, 22, 23.
- Production-span transfer hypothesis: preparation (source journal; retained in research archive) — slides 7, 22, 23.
- Full production-span bytes pass while PBS exits unsuccessfully (source journal; retained in research archive) — slides 7, 22, 23.
- Production-span pilot 224116 submitted (source journal; retained in research archive) — slides 7, 22, 23.
- A filesystem fingerprint is local; draft content needs a portable identity (source journal; retained in research archive) — slides 7, 22, 23.
- 23 October: submit a correctness-first H200 EAGLE3 comparison (source journal; retained in research archive) — slides 7, 22, 23.
- A shell exit can fail after successful native transport (source journal; retained in research archive) — slides 7, 22, 23.
- Whole registered buffers are different from per-request metadata rows (source journal; retained in research archive) — slides 7, 22, 23.
- Nonlogin repair 224157 is submitted for real confirmation (source journal; retained in research archive) — slides 7, 22, 23.
- Real confirmation of the nonlogin launcher repair (source journal; retained in research archive) — slides 7, 22, 23.
- Preserve strict errors while repairing the launcher environment (source journal; retained in research archive) — slides 7, 22, 23.
- 24 October: EAGLE3 improves decode spacing but fails the TTFT gate (source journal; retained in research archive) — slides 7, 22, 23.
- 24 October: separate H200 token identity, KV screening, and H100 numerical evidence (source journal; retained in research archive) — slides 7, 22, 23.
- 24 October: decode-only EAGLE3 candidate 25988 submitted (source journal; retained in research archive) — slides 7, 22, 23.
- 24 October: decode-only EAGLE3 run exposes role-specific KV geometry (source journal; retained in research archive) — slides 7, 22, 23.
- 24 October: submit the role-aware KV validation retry (source journal; retained in research archive) — slides 7, 22, 23.
- 25 October: decode-only EAGLE3 passes the short SLA but loses throughput (source journal; retained in research archive) — slides 7, 22, 23.
- H100 equal-TP EAGLE benchmark submitted and running (source journal; retained in research archive) — slides 7, 22, 23.
- 29 October: full shallow EAGLE loses; portable readers confirmed on compute (source journal; retained in research archive) — slides 7, 22, 23.
### Graph, chunk, attention and cache choices

- Native kernel pilot import failure and controlled cache repair (source journal; retained in research archive) — slides 17, 21, 26, 28, 30.
- H100: smaller HPC-Ops prefill chunks (source journal; retained in research archive) — slides 17, 21, 26, 28, 30.
- 20 October 2026: repeated N60 gain, latency failure attribution and observed polling trials (source journal; retained in research archive) — slides 17, 21, 26, 28, 30.
- Close the unobserved polling check and screen native FP8 linear kernels (source journal; retained in research archive) — slides 17, 21, 26, 28, 30.
- 21 October — H200 receive interval 2 has no useful demonstrated gain (source journal; retained in research archive) — slides 17, 21, 26, 28, 30.
- Submit a cheaper native TP4 prefill graph probe — 21 October 2026 (source journal; retained in research archive) — slides 17, 21, 26, 28, 30.
- Separate the graph-policy effect from speculative decoding (source journal; retained in research archive) — slides 17, 21, 26, 28, 30.
- Two H200 policy controls queued without displacing EAGLE correctness (source journal; retained in research archive) — slides 17, 21, 26, 28, 30.
- Submit full N64 prefill chunks after closing the load bracket (source journal; retained in research archive) — slides 17, 21, 26, 28, 30.
- Close smaller chunks after one slower pass and one actual SLA failure (source journal; retained in research archive) — slides 17, 21, 26, 28, 30.
- 29 October: cap64 is valid but below the useful-gain gate (source journal; retained in research archive) — slides 17, 21, 26, 28, 30.
- Cold-prefill cache implementation pair: sub-1% result (source journal; retained in research archive) — slides 17, 21, 26, 28, 30.
- 29 October: cold-prefill cache candidate and fresh control submitted (source journal; retained in research archive) — slides 17, 21, 26, 28, 30.
- 29 October: actual full decode-cap submission and a positive compile prerequisite (source journal; retained in research archive) — slides 17, 21, 26, 28, 30.
- 29 October: interval 2 loses; keep interval 4 and inspect actual hardware/accounting (source journal; retained in research archive) — slides 17, 21, 26, 28, 30.
- 29 October: close the full transfer polling bracket (source journal; retained in research archive) — slides 17, 21, 26, 28, 30.
- 29 October: three full KV completion polling jobs actually submitted (source journal; retained in research archive) — slides 17, 21, 26, 28, 30.
- Final report: close sparse graph trial and retain the reproduced service (source journal; retained in research archive) — slides 24, 28.
### Other track

- H100 HPC-Ops prefill chunk interaction: actual submissions (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- 22 October: defer a controlled transport comparison until baseline and cost coordination (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- 22 October: completed method/rank-density baselines change the two-node priority (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- 22 October: recovered native OpenFOAM evidence and shared CPU queue coordination (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- 22 October: statically qualify the partition-preserving CPU binding experiment (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- 22 October: preserve partitions and screen rank-to-NUMA placement without cluster spending (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- 22 October: full native review of shared one- and two-node Scotch runs (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- A balanced placement option and a real explanation of the pending queue (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- Checking the locality trade-off before spending on a larger test (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- A four-node placement candidate and a cheap MPI interface preflight (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- 23 October: recover six four-node records and replace the provisional scaling story (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- 23 October: teach the complete HPC journey and preserve presentation knowledge (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- HPC presentation allocation and reproducible CPU submission — 23 October 2026 (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- Expand the CPU campaign and resolve the observed post-init affinity failure (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- Independent repeat improves the observed mean; topology qualification still blocks placement (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- 26 October: close launcher syntax changes and identify the affinity caller (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- 26 October: apparent zyx gain requires an order control (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- 26 October: use both CPU clusters and review the Iris Scotch partition (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- 26 October: fresh initialization passes and matched timing resumes (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- 26 October: select zyx from fresh controls and preserve raw cuts (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- 26 October: reject the Iris Scotch loss and add a fresh hierarchical control (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- 26 October: reverse the order before promoting the apparent gain (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- 26 October: xyz completes while the matched zyx screen continues (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- 27 October: native affinity query observed, setter still unidentified (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- Iris full150 pair 2294234: actual fallback measurement admitted (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- 27 October: all 512 main threads pass post-initialization placement qualification (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- Native NSCC transfer bundle ready offline; actual admission blocked (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- Plan: transfer the promising HPC hypotheses to NSCC CPU (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- 27 October: qualify explicit CPU placement after MPI initializes (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- 27 October: move the qualified pin mechanism into the real Pstream boundary (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- 27 October: submit the real OpenFOAM integration qualification (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- 27 October review: the zyx advantage survives execution-order reversal (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- 27 October: later-step behavior survives the 50-step horizon (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- 27 October: extend the preferred zyx candidate to later steps (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- 28 October: align the AI submission with reproduced N64 while preserving HPC (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- Full-length Iris order result and reversed confirmation (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- NSCC target, access attempts and partial order confirmation (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- Correct VPN readiness and assess the first reversed arm (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- Graph screen review and actual reversed confirmation (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- Graph-derived rank placement submitted as Iris 2294366 (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- Actual affinity evidence selects a graph placement candidate (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
- Full reverse-order result rejects the large order-gain claim (source journal; retained in research archive) — Independent HPC record; excluded from AI coverage.
### Operations and documentation

- H100 access restored, complete results and next controlled question (source journal; retained in research archive) — slides 4, 9, 31.
- N62 terminal review and presentation update — 20 October 2026 (source journal; retained in research archive) — slides 4, 9, 31.
- Complete N62 submission and semantic replay gate — 21 October 2026 (source journal; retained in research archive) — slides 31.
- 21 October: native multi-region registration and host auxiliary hypothesis (source journal; retained in research archive) — slides 4, 9, 31.
- Native registration and host auxiliary gate: definite GPU receipt (source journal; retained in research archive) — slides 4, 9, 31.
- Registration wording and corrected scope inference — 2026-10-21T02:11:16.205433+00:00 (source journal; retained in research archive) — slides 4, 9, 31.
- Resolve shared-context ownership before continuing AI — 21 October 2026 (source journal; retained in research archive) — slides 4, 9, 31.
- Restored access and sealed native prefill timeout — 21 October 2026 (source journal; retained in research archive) — slides 4, 9, 31.
- 22 October: native registration and host auxiliary transport pass (source journal; retained in research archive) — slides 4, 9, 31.
- 22 October: update the research talk from sealed results (source journal; retained in research archive) — slides 4, 9, 31.
- 22 October: publish the reviewed research talk (source journal; retained in research archive) — slides 4, 9, 31.
- Exit-boundary payload ready; access fails before submission (source journal; retained in research archive) — slides 4, 9, 31.
- 23 October: use existing H100 access and reconcile the last component probe (source journal; retained in research archive) — slides 4, 9, 31.
- 23 October: turn retained technical history into an explainable research story (source journal; retained in research archive) — slides 4, 9, 31.
- Real FP8 kernels, real EAGLE outputs, and a revised H100 allowance (source journal; retained in research archive) — slides 4, 9, 31.
- Actual prefill graph use: retained legacy versus modern evidence (source journal; retained in research archive) — slides 4, 9, 31.
- H100 existing-access check — 26 October 2026 (source journal; retained in research archive) — slides 4, 9, 31.
- H100 access restored and selected AI budget refreshed (source journal; retained in research archive) — slides 4, 9, 31.
- Use the full actual H100 balance without an internal SU buffer (source journal; retained in research archive) — slides 4, 9, 31.
### Runtime, portability and reader recovery

- Repair the H200 microbenchmark bind path (source journal; retained in research archive) — slides 31.
- 21 October — CPU-validated Bash dispatch repair submitted (source journal; retained in research archive) — slides 31.
- 23 October: real H200 reference failed before the token client started (source journal; retained in research archive) — slides 4, 25, 31.
- Fully verify draft bytes in each role's filesystem view (source journal; retained in research archive) — slides 25, 31.
- Repair a launcher error without blaming EAGLE performance (source journal; retained in research archive) — slides 31.
- 28 October Vietnam time: repair the client launch and preserve failed chunk trials (source journal; retained in research archive) — slides 4, 25, 31.
- Four jobs submitted after correcting native GPU visibility (source journal; retained in research archive) — slides 4, 25, 31.
- Runtime storage becomes the current prerequisite (source journal; retained in research archive) — slides 4, 25, 31.
### Startup and resource-cost hypotheses

- Independent reverse-order startup-prefetch confirmation (source journal; retained in research archive) — slides 18.
- Bounded H100 startup-cost experiment (source journal; retained in research archive) — slides 18.
### Tokenization, routing and collectives

- Native prefill routing pair: submitted (source journal; retained in research archive) — slides 11, 21, 26.
- 20 October 2026: confirm the runner interaction and screen the next costs (source journal; retained in research archive) — slides 11, 21, 26.
- 21 October — one controlled H200 routing candidate retains a queue position (source journal; retained in research archive) — slides 11, 21, 26.
- H200 routing follow-up: fresh round-robin versus power-of-two (source journal; retained in research archive) — slides 5, 11, 21.
- Native fusion screens admitted; five own H200 jobs (source journal; retained in research archive) — slides 11, 21, 26.
- Phase-isolated native QK normalization and RoPE fusion (source journal; retained in research archive) — slides 11, 21, 26.
- Matched H200 routing pair submitted (source journal; retained in research archive) — slides 11, 21, 26.
- 28 October: reproduce approximately 3k throughput and test prefill tokenization (source journal; retained in research archive) — slides 11, 21, 26.
- Fresh control, BF16 diagnostic and an independent backend control (source journal; retained in research archive) — slides 11, 21, 26.
- 28 October 2026 14:44 Vietnam time: distinguish semantic success from a successful warmup step (source journal; retained in research archive) — slides 11, 21, 26.
- Small tuning branches close; real submission replay exposes and repairs a reader bug (source journal; retained in research archive) — slides 11, 21, 26.
### Research method and decisions

- Research priorities after the upstream review (source journal; retained in research archive) — slides 9, 24, 32.
- 22 October: close N60 losses and preserve phase-aligned evidence (source journal; retained in research archive) — slides 9, 21.
- A five-job wave with separate numerical, precision and transport questions (source journal; retained in research archive) — slides 9, 21.
### Transport, KV and semantic correctness

- 21 October — full PD eager-prefill correctness repair submitted (source journal; retained in research archive) — slides 7, 8, 22.
- 21 October — native full-PD readiness passes, launcher regression blocks output (source journal; retained in research archive) — slides 7, 8, 22.
- 21 October — actual native PD request exposes transport and warmup-gate failures (source journal; retained in research archive) — slides 7, 8, 22.
- 21 October: real descriptor gate passes; next inspect native registration and aux (source journal; retained in research archive) — slides 7, 8, 22.
- 21 October: isolate native KV descriptor mechanics before another full model (source journal; retained in research archive) — slides 7, 8, 22.
- 21 October: submit the bounded actual KV descriptor gate (source journal; retained in research archive) — slides 7, 8, 22.
- 21 October — base NIXL VRAM writes pass; preserve a collection-layout correction (source journal; retained in research archive) — slides 7, 8, 22.
- 21 October — cheap real NIXL peer/VRAM gate replaces an unchanged model retry (source journal; retained in research archive) — slides 7, 8, 22.
- 21 October: require actual per-pair completion evidence before warmup success (source journal; retained in research archive) — slides 7, 8, 22.
- Uniform eager TP4 prefill reaches native readiness — 21 October 2026 (source journal; retained in research archive) — slides 7, 8, 22.
- 22 October: make the next native EAGLE3 failure diagnosable (source journal; retained in research archive) — slides 7, 8, 22.
- 23 October: production geometry narrows the uncertainty without another GPU startup (source journal; retained in research archive) — slides 7, 22, 23.
- 23 October: spend a bounded four-GPU probe on the actual missing geometry (source journal; retained in research archive) — slides 7, 23.
- 23 October: a suspicious intermediate list was not a proven transport bug (source journal; retained in research archive) — slides 7, 8, 22.
- Configured concurrency and bounded first-transfer initialization (source journal; retained in research archive) — slides 7, 12, 31.
- Current H100 control and equal-TP EAGLE functional pass (source journal; retained in research archive) — slides 7, 16, 23.
- Close the full graph/admission study and accept a small transport component (source journal; retained in research archive) — slides 7, 8, 22.
- 28 October 2026 16:31 Vietnam time: keep full trials queued and add distinct prerequisites (source journal; retained in research archive) — slides 7, 8, 22.
- 29 October: preserve the observer source-location failure before deriving a fix (source journal; retained in research archive) — slides 7, 8, 22.
### Replication, load and regime recovery

- 21 October: accepted short load gain proceeds to full matched confirmation (source journal; retained in research archive) — slides 10, 12, 25.
- 21 October: queue full N62 control and N64 candidate (source journal; retained in research archive) — slides 10, 12, 25.
- 21 October — independent H200 N62 point reproduces within 0.04% (source journal; retained in research archive) — slides 10, 12, 25.
- 21 October — actual partition ceiling repairs the next load-screen design (source journal; retained in research archive) — slides 10, 12, 25.
- 22 October: fresh full N62 control and the initial SLA-failure cohort (source journal; retained in research archive) — slides 10, 12, 25.
- 22 October: inspect all rank traces before choosing another algorithm change (source journal; retained in research archive) — slides 10, 12, 25.
- 22 October: full N64 evidence and interpretation (source journal; retained in research archive) — slides 10, 12, 25.
- 22 October: inspect the matched N62/N64 improvement beyond score (source journal; retained in research archive) — slides 10, 12, 25.
- 22 October: full N64 passes and the next guarded load screen is frozen (source journal; retained in research archive) — slides 10, 12, 25.
- 22 October: full N64 repeats within 0.014% (source journal; retained in research archive) — slides 10, 12, 25.
- 22 October: independent full N64 replication (source journal; retained in research archive) — slides 10, 12, 25.
- 22 October: independent full N64 submitted (source journal; retained in research archive) — slides 10, 12, 25.
- 22 October: prepare a guarded next load question while full confirmation runs (source journal; retained in research archive) — slides 10, 12, 25.
- 22 October: freeze a full matched N64/N68 comparison (source journal; retained in research archive) — slides 10, 12, 25.
- 22 October: full N64/N68 receipts (source journal; retained in research archive) — slides 10, 12, 25.
- 22 October: guarded N68 screen submitted (source journal; retained in research archive) — slides 10, 12, 25.
- 22 October: short N68 gain supports full matched confirmation (source journal; retained in research archive) — slides 10, 12, 25.
- 23 October: the short N68 gain shrinks in full confirmation (source journal; retained in research archive) — slides 10, 12, 25.
- Research milestone — 25 October 2026: close the N66–N72 load branch (source journal; retained in research archive) — slides 10, 12, 25.
- Research milestone — 25 October 2026: bounded H200 closed-loop load sweep (source journal; retained in research archive) — slides 10, 12, 25.
- Research milestone — 25 October 2026: five H200 jobs admitted (source journal; retained in research archive) — slides 10, 12, 25.
- Full native-runtime load bracket after graph/admission review (source journal; retained in research archive) — slides 10, 12, 25.
- Close full native N62/N66 without an improvement (source journal; retained in research archive) — slides 10, 12, 25.
- Restore a fresh H100 control and repair equal-TP observation (source journal; retained in research archive) — slides 16, 23.
- Preserve and isolate the 3k incumbent (source journal; retained in research archive) — slides 10, 12, 25.
- Full incumbent recovery admitted: 26313 → 26315 → 26317 → 26319 (source journal; retained in research archive) — slides 10, 12, 25.
- Legacy N64 full replay: valid local result, lower than the old cluster (source journal; retained in research archive) — slides 10, 12, 25.
- Actual incumbent runtime re-established in running job 26313 (source journal; retained in research archive) — slides 10, 12, 25.
- Prepare an offline full-run reviewer before recovery results arrive (source journal; retained in research archive) — slides 25, 31.
- H200 routing/fusion results and incumbent configuration correction (source journal; retained in research archive) — slides 10, 12, 25.
- S68 job 26308 failed at source identity, not transport (source journal; retained in research archive) — slides 10, 12, 25.
- S68r2: correct the native source mount before another allocation (source journal; retained in research archive) — slides 10, 12, 25.
- S68r2 submitted as 26337; full incumbent replay is running (source journal; retained in research archive) — slides 10, 12, 25.
- Full modern H200 control: valid, no new improvement (source journal; retained in research archive) — slides 10, 12, 25.
- S73 completes the prefill graph/admission factorial (source journal; retained in research archive) — slides 10, 12, 25.
- Submit missing graph/admission cell as job 26347 (source journal; retained in research archive) — slides 10, 12, 25.
### Topology and layout

- 22 October: withhold P12/D4 after source-level transport review (source journal; retained in research archive) — slides 5, 6, 8, 26.
- 24 October: close a measured cache loss and fix the next topology prerequisite (source journal; retained in research archive) — slides 5, 6, 8, 26.
- Failed S62 routes: bounded source diagnosis (source journal; retained in research archive) — slides 5, 6, 8, 26.
- 25 October: prepare a modern-runtime two-replica TP4 decode screen (source journal; retained in research archive) — slides 5, 6, 8, 26.
- 25 October: S62 two-replica TP4 decode screen queued as 26055 (source journal; retained in research archive) — slides 5, 6, 8, 26.
- Research milestone — 25 October 2026: S62r2 failed before its worker script (source journal; retained in research archive) — slides 5, 6, 8, 26.
- 25 October: submit corrected two-replica TP4 topology as 26057 (source journal; retained in research archive) — slides 5, 6, 8, 26.
- 25 October: correct S62 route warmup before GPU allocation (source journal; retained in research archive) — slides 5, 6, 8, 26.
- Research milestone: job 26076: ready workers, semantic-route timeout, no benchmark (source journal; retained in research archive) — slides 5, 6, 8, 26.
- Research milestone — 25 October 2026: prepare corrected S62r3 topology screen (source journal; retained in research archive) — slides 5, 6, 8, 26.
- Research milestone — 25 October 2026: corrected S62r3 topology retry submitted (source journal; retained in research archive) — slides 5, 6, 8, 26.
- S62r4 job 26081: partial routes, bounded timeout, no benchmark (source journal; retained in research archive) — slides 5, 6, 8, 26.
- S62r4 submitted as job 26081 (source journal; retained in research archive) — slides 5, 6, 8, 26.
### Model compile and prerequisites

- 29 October: native compile observer prerequisite actually submitted (source journal; retained in research archive) — slides 26, 31.
- 29 October: corrected source-pinned observer admitted as 27340 (source journal; retained in research archive) — slides 26, 31.
- 29 October: review the fresh control and admit a native CPU cache prerequisite (source journal; retained in research archive) — slides 26, 31.
- Full Qwen compile exposes an unsupported RoPE/KV interface (source journal; retained in research archive) — slides 26, 31.
- 29 October: actual Qwen compilation startup qualification with conditional benchmark (source journal; retained in research archive) — slides 26, 31.
- 29 October: token-count source provenance and the next compile prerequisite (source journal; retained in research archive) — slides 26, 31.

## Limits and use in the talk

Use the main talk to explain why the team changed direction, what control made a result interpretable, what failed and what was learned. Use speaker notes and this index for questions about a particular run. No startup, CPU primitive or library-feasibility result is promoted to a serving improvement. Official model-quality acceptance remains unverified.

This audit does not certify every retained historical claim, fill missing original reasoning, or resume research. No new job, authentication or HPC update is performed.
