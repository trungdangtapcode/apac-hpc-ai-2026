# AI talk plan and HPC handoff

**AI target: 12:30 (750 seconds), including pauses.** This is an estimated rehearsal target, not an observed mock duration. The English script is about 1,400 spoken words, intended for roughly 115–125 words per minute plus slide changes and short pauses. The public slot is 15–20 minutes for the combined AI and HPC talk, followed by 10 minutes of Q&A. If the team uses the full 20 minutes, this target leaves about 7:30 for HPC. If only 15 minutes are available, agree on a shorter AI cut with the HPC presenter before rehearsal; do not assume this plan fits both talks in that slot.

The route preserves the 16 main AI slides and their order. Script headings use the exact current slide titles in the reasoning plan. The spoken script adds the reasoning that connects the existing visual evidence; it does not claim experiments or profiling that did not happen.

## Three investigation stories

1. **Feasible deployment (slides 1–7):** What does the workload require, which layout could serve both phases, and why did a warmup failure lead to a narrow KV-transfer setup change? Separate the practical topology choice from the historical descriptor patch. The CPU equivalence checks and patched N32 run establish feasibility, not an isolated descriptor speedup.
2. **Backend and load selection (slides 8–12):** What evidence gives leads without proving a bottleneck? Why test a matched decode implementation, what throughput/latency tradeoff did it show, and why retain N64 instead of N68? Distinguish the diagnostic profile from the separate controlled service experiment.
3. **Robustness and quality (slides 13–16):** Does the portable package complete, do selected H100-derived settings transfer to H200, and do rejected proxy improvements survive whole-service evaluation? Close with the package performance result, the full local quality-retention result and three bounded decisions. Detailed quality counts belong in backup 19.

Existing SGLang, NIXL, DeepGEMM, FlashInfer and HPC-Ops are reused components. The engineering contribution is local integration and a bounded request-scoped metadata change to one NIXL transfer path, plus controlled selection and validation. Do not claim the team invented these libraries or established a first-in-the-world result.

## Per-slide timing

| Main slide | Target | Cumulative | Speaking purpose |
|---|---:|---:|---|
| 1 | 0:40 | 0:40 | State workload, SLA and why raw speed is insufficient |
| 2 | 0:35 | 1:15 | Separate decision, implementation and measured finding |
| 3 | 0:50 | 2:05 | Explain the feasible topology choice and its limits |
| 4 | 0:45 | 2:50 | Explain where prompt, decode and temporary KV state move |
| 5 | 0:45 | 3:35 | Locate the historical failure before scoring |
| 6 | 0:55 | 4:30 | Explain why request-scoped descriptors were a cheap first hypothesis |
| 7 | 0:50 | 5:20 | State what the patch established and what counterfactual is missing |
| 8 | 0:50 | 6:10 | Use profiling as a lead, not causal proof |
| 9 | 0:45 | 6:55 | Introduce a separate matched backend experiment |
| 10 | 0:55 | 7:50 | Explain the throughput gain, latency tradeoff and repeat |
| 11 | 0:50 | 8:40 | Explain the N64 operating-point decision and N68 rejection |
| 12 | 0:40 | 9:20 | Describe request-level misses without inventing their cause |
| 13 | 0:55 | 10:15 | Separate portable package acceptance from optimisation |
| 14 | 0:55 | 11:10 | Explain direct H200 transfer checks and the useful-gain gate |
| 15 | 0:40 | 11:50 | Reject proxy-only improvements |
| 16 | 0:40 | 12:30 | State the three lessons, quality result and HPC handoff |
| **Total** | **12:30** | **12:30** | **Estimated target; no live mock has been timed** |

The word-count and timing targets are estimates. Practice aloud with natural pauses and slide changes, then record the actual duration and revise only after the team has rehearsed.

## Route, terminology and claims

The PowerPoint has 16 main AI slides, AI backups and eight HPC slides. Present AI 1–16, then hand control to the HPC presenter. AI backup 19 is titled **“Backup · full-set accuracy verification”** and contains the full-set quality counts, interpretation and local-certification boundary. Open it only for a relevant question. Do not read the entire topology list or all nine late-run job details aloud.

Explain KV as temporary attention state that lets generation continue. Explain a descriptor as an address-range list, not the transferred data. Call NIXL an existing transfer library; the team's change is a bounded, request-scoped metadata change in its integration path.

For the three stories, lead with the observation and why it mattered, then state what changed, what the evidence supports and what remains unknown. Slides 3–4 explain the prefill/decode resource tradeoff; do not read out topology examples. Slides 5–7 cover the historical failure, request-address hypothesis, correctness invariant and actual patched-path usability. The main script omits the 403.8-million/188 scope illustration and detailed N32 submetrics; use backup 20 for source scale and backup 21 for the recovery evidence. There is no unpatched scored control or isolated descriptor speedup.

Slides 8–12 distinguish a diagnostic profile from the separate matched backend test and the full-load N64/N68 decision. The decode result is about +5.30% good output throughput, with mean TTFT +125 ms and mean ITL −1.64 ms; N64 repeated, while full N68's +0.08% was below the usefulness gate. Slide 13 explains the readiness-to-real-requests-to-client-reader-and-cleanup chain and uses job 28197 as package acceptance, not optimization. Historical and native performance comparisons belong in backup 31. Slide 14 says the matched H200 chunk trial recovered part of the H100-derived branch but stayed 4.52% below the incumbent; phase-mode gains were below 0.14%, and no candidate cleared the 1% gate. Do not say all alternatives were below control.

Slide 16 closes with three lessons: choose the phase split and backend for the target hardware; keep full, repeated gains; and verify deployment and answer quality separately. Its main evidence is accepted package performance and the full local quality-retention result. State the local point-gate pass, not BTC certification. Full quality counts remain in backup 19.

Use [TALK_SCRIPT_EN.md](TALK_SCRIPT_EN.md) or [TALK_SCRIPT_VI.md](TALK_SCRIPT_VI.md) to rehearse. [TRANSCRIPT_VI.md](TRANSCRIPT_VI.md) remains the detailed visual and terminology guide; [MOCK_QA_EVIDENCE.md](MOCK_QA_EVIDENCE.md) has result links and limits. The target is a spoken explanation, not a folder tour. No live slideshow test or human mock is claimed.
