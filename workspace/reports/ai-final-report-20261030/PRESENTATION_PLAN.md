# Compact AI investigation and protected OpenFOAM handoff

The official combined time and whether it includes Q&A have been requested from the owner and are not yet supplied. The earlier 15–20 minute AI-only allowance is historical context, not permission to consume the whole combined session. This plan proposes a compact AI route of about 10 minutes 40 seconds, with an explicit rehearsal stop by 12 minutes. These are preparation targets, not organiser limits or recorded timings. The independent HPC presenter must agree their time before the mock.

## Three technical stories

- Engineering decision: choose a feasible split of the fixed 16-H200 budget, explaining replica/TP tradeoffs and eligibility before scores.
- Team implementation: target an observed cold transfer setup failure; change request-scoped descriptors and show exactly what CPU and real serving evidence prove.
- Experimental findings: reuse phase-specific GPU implementations, test a matched full service change, and choose client concurrency using full trials and repetition.

The four research questions remain: resource distribution, performance limits, SLA-qualified interventions and robustness. Each story follows problem → observation → prioritisation/hypothesis → intervention/control → evidence → supported decision/limit. Eligibility, feasibility and performance are different claims.

## Rehearsal targets

| Slide | Spoken purpose | Target |
|---|---|---:|
| 1 | Fixed task and success criterion | 0:35 |
| 2 | What we own, reuse and learned; how the investigations relate | 0:30 |
| 3 | Resource tradeoff and what topology evidence permits | 0:40 |
| 4 | Retained architecture and added transfer cost | 0:35 |
| 5 | Concrete failure before scoring | 0:40 |
| 6 | Why setup first; exact patch and CPU checks | 0:50 |
| 7 | Real patched outcome and missing causal comparison | 0:45 |
| 8 | Profile-driven hypotheses, not assumed bottlenecks | 0:45 |
| 9 | Matched implementation test and held-fixed factors | 0:40 |
| 10 | Goodput/TTFT/ITL tradeoff and independent repeat | 0:50 |
| 11 | Full N64 result, repeat and N68 stopping rule | 0:45 |
| 12 | Which request-level condition still fails | 0:40 |
| 13 | Why repeated evidence wins over an isolated peak | 0:40 |
| 14 | One cross-platform forecast and incomplete uncertainty | 0:40 |
| 15 | Reject proxy improvements that lose service throughput | 0:35 |
| 16 | Remaining validation and handoff to OpenFOAM | 0:30 |

Total target: 10:40. Reserve the gap to 12:00 for navigation, transitions and natural delivery. If the total session is shorter, reduce optional cross-platform/negative-trial detail first; do not erase the missing-evidence statements or consume the HPC presenter’s slot. Confirm the actual combined allocation and Q&A rule before setting the final script length.

## Slide-show navigation

The PowerPoint contains 40 physical slides. AI 1–16 is the main talk. AI backups 17–32 are hidden in normal slide-show mode; after 16 the show advances to the unchanged OpenFOAM slide 33, continuing through 40. Backups remain available through the slide navigator for questions. Test this once in the actual presentation application; artifact validation checks the hidden flags, not the live screen-sharing application.

TripleU_APAC2026_Main_Talk.pdf contains the 24 visible pages in presentation order: AI 1–16 followed by HPC 33–40. The full 40-page PDF retains the AI backups for Q&A. If presenting from the full PDF, jump to page 33 after AI 16; PDF readers do not follow PowerPoint hidden-slide flags.

## Speak the inference, not the table

For each main slide, state why the question matters, one decisive observation and the decision it supports. Use the short brief if time is tight; use the longer script only for rehearsal and questions. Do not read every job ID, every metric or the complete configuration row. Say “the evidence motivated this test” when it does not establish the causal bottleneck.

The AI speaker owns the AI claims. A support member can supply the exact source/control/limit. Hand OpenFOAM questions to its independent owner; do not improvise CPU causality. Use MOCK_QA_EVIDENCE.md for cross-examination, and record actual timing/feedback only after the human mock occurs.
