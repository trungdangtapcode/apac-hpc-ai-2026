# AI talk plan and HPC handoff

**Official slot:** the public rule is a combined AI and HPC talk of 15–20 minutes, followed by 10 minutes of Q&A. The team must agree the split. This plan targets about 10–11 minutes for AI and leaves at least 4 minutes for OpenFOAM inside a 15-minute talk. The team must time the combined rehearsal; these are targets, not performed timings. The actual invitation has not been inspected.

## Investigation flow

1. **Constraint and decision (slides 1–4).** The 16 H200s occupy two nodes. The goal is useful output throughput subject to request latency and a joint success fraction. FP8 geometry, worker startup and networked KV transfer determine which layouts are eligible. The 17 usable topology observations document feasibility and tradeoffs. Because load levels and histories differ, they do not establish a uniform topology winner. Retain the two TP4/EP1 prefill workers plus TP8/EP8 decode as a practical, compatible, repeatably usable operating layout—not a global optimum.
2. **A setup failure and a bounded repair (slides 5–7).** In one historical heterogeneous-TP recovery branch, both model workers were ready but pair warmup timed out before AIPerf. Source inspection exposed whole-pool descriptor enumeration, so the team chose a narrow request-scoped change with a cheap byte-range equivalence check. The CPU check and successful patched serving run justify feasibility. Missing unpatched scored control means no descriptor-only speedup or proof that descriptors were the dominant system bottleneck.
3. **Diagnose, then test a separate serving hypothesis (slides 8–10).** The N48 profile names candidate areas; summed kernel durations are not a wall-time budget. The N64 first-token failures identify a latency symptom but not its cause. The decode implementation comparison is a separate supported, controlled probe motivated by candidate kernel directions. Its measured gain comes from the matched full control and repeated treatment, not from the profile percentages.
4. **Select an operating point and test robustness (slides 11–16).** Full N62/N64 comparison and an independent N64 repeat support the selected client load; the N68 short-test gain does not survive the full test. Request-level evidence shows which SLA condition failed. Repeated results, rejected proxy wins, direct H100-derived tests on H200, and a final full replay of the repaired packaged entry keep the conclusion bounded. Slide 14 reports direct transfer evidence; slide 16, “Preserve the model; optimise the serving path,” reports the accepted portable serving configuration and its workload performance. A brief Q1 line states that the official FP8 checkpoint is retained for the organiser-run full-set evaluation. The earlier one-point forecast is backup 33; all nine late H200 jobs are backup 34; the exact 28194 readiness failure and 28197 acceptance are backup 31.

## Timing guide

| Main slides | Target | What the audience should learn |
|---|---:|---|
| 1–2 | 0:55 | Objective, SLA and which claims are team decisions, implementation or measured findings |
| 3–4 | 1:25 | Why the retained split is feasible and useful; why the topology search does not prove a global winner |
| 5–7 | 2:15 | Failure symptom, why the bounded source hypothesis came first, actual patch evidence and missing counterfactual |
| 8–10 | 2:15 | Profile limits, separate controlled decode probe, throughput/latency tradeoff and repeat |
| 11–13 | 2:10 | N64 decision, request-level tails and repeated evidence |
| 14–15 | 1:15 | Direct H100-to-H200 transfer outcome and rejected alternatives |
| 16 | 0:35 | Preserved model, serving-only work and explicit OpenFOAM handoff |
| **Total** | **10:50** | Target only; rehearse aloud and time it |

If the team is allotted only 15 minutes total, keep AI within about 10:50 and give HPC at least four minutes; trim optional details from slides 13–15, never the evidence or HPC handoff. The questions receive their separate 10-minute Q&A slot.

## Main route and backups

The PowerPoint contains 42 physical slides. Present AI slides 1–16, then hand control directly to HPC slide 35. AI backups 17–34 are hidden in normal slideshow mode and opened through the slide navigator only when a question calls for them. Slide 33 preserves the historical held-out H100-to-H200 forecast; slide 34 summarises nine final H200 allocations. The main-talk PDF has 24 pages: AI 1–16 followed by HPC 35–42. In the full PDF, jump from page 16 to page 35. HPC slide content belongs to its independent presenter.

Before the actual talk, verify this route in the presentation application, including opening hidden backups and returning to the main sequence. The PDFs and hidden flags document intended navigation; they do not prove a live screen-sharing test.

## Speaking and Q&A method

At each transition say: the problem that matters to the SLA; what the observation shows; why this test was selected; what decision the measurement supports; what it does not prove. Do not read the whole table. On slides 3–4 explicitly say there is no matched all-topology ranking. On slides 5–7 say descriptor enumeration was a source-visible, cheap-to-check first hypothesis—not a proven bandwidth/layout/scheduling exclusion. On slide 8→9 introduce a separate controlled decode probe, not a fix supposedly deduced from percentages.

The AI presenter owns the AI numbers. Use [TALK_SCRIPT_EN.md](<TALK_SCRIPT_EN.md>) or TALK_SCRIPT_VI.md (source: `TALK_SCRIPT_VI.md`, retained outside this compact package) to rehearse, then the bilingual per-slide guide (source: `TRANSCRIPT_VI.md`, retained outside this compact package) to learn diagrams and terms. Use [MOCK_QA_EVIDENCE.md](<MOCK_QA_EVIDENCE.md>) for evidence links and limits. Hand OpenFOAM solver, rank-count and variability questions to its presenter. Record actual rehearsal duration and audience feedback only after the team performs it.
