# Teacher Thanh requirement audit — 1 November 2026

**Historical edition/assessment:** superseded for current material by the [1 November final AI revision](../../submission-review/ai-final-update-20261101/REQUIREMENT_CLOSURE.md). The actual teacher-audit reasoning gaps are corrected; human rehearsal remains unverified. Original dated content below is retained.

Reviewed 2026-11-01T11:59:59.278098+07:00, Vietnam time (UTC+7). **Verdict: substantially aligned, not fully satisfied.** This is an AI presentation audit against the owner's exact `/home/apacsc42/requirement.md`, not a certification of the separate HPC worker's technical claims or of delivery readiness.

## What was inspected

- [Current PowerPoint](../../VNUHCM%20-%20TripleU/Presentation/TripleU_APAC2026_Presentation.pptx): 16 main AI slides, 16 hidden AI backups and eight unchanged HPC slides.
- [Main-talk PDF](../../submission-review/ai-investigation-update-20261030/TripleU_APAC2026_Main_Talk.pdf): the 16 main AI slides were visually inspected using a rendered contact sheet.
- [English transcript](../ai-final-report-20261030/TRANSCRIPT_EN.md), [Vietnamese transcript](../ai-final-report-20261030/TRANSCRIPT_VI.md), [presentation plan](../ai-final-report-20261030/PRESENTATION_PLAN.md) and [source-linked Q&A](../ai-final-report-20261030/MOCK_QA_EVIDENCE.md).
- Independent bounded review of topology justification, KV prioritisation, profiling scope and transitions. This supplements, rather than replaces, the actual deck and transcript inspection.

PowerPoint slide order was resolved through presentation relationships with python-pptx. ZIP part names such as `slide1.xml` are not a reliable display-order index in the merged deck. Visual inspection used the current main-talk PDF; actual Office playback/projector readability and a human rehearsal were not performed.

Requirement SHA-256: `c5501a44540ca7d3834e731dac3472afacdf1d5505cabdfdaf2d29809323ae20`.

Presentation SHA-256: `dcc56658f7efa1b43294d32316de4eb27c65d765d2a9f1806e18c67a40ca9d13`.

## Requirement-by-requirement assessment

The supplied requirements number stages 1, 2, 3, 4, 6 and 7; no stage 5 is invented here. PASS means prepared material supports that requirement, not that human delivery was verified.

| Teacher requirement | Assessment | Evidence and remaining limit |
|---|---|---|
| Stage 1: problem, baseline, bottleneck, priority, hypothesis, intervention, evidence, conclusion | PARTIAL | Slides 1–4 establish objective and architecture; 5–7 give a bounded setup case; 8–15 cover profiling, controlled experiments and robustness. Three selection/transition gaps below remain. |
| Stage 2: distinguish engineering decisions, contributions and findings; avoid unsupported causality | PASS for claim framing | Slide 2 explicitly separates the claim classes. Slide 7 states descriptor-only end-to-end speedup is unknown. Slides 8 and 16 bound profiling and quality claims. |
| Stage 3: one message, explanatory diagrams, decisive evidence and appendix | SUBSTANTIALLY MET | Architecture, failure pipeline, descriptor before/after, controlled comparison and latency scatter carry the reasoning. Titles state the point; detailed evidence sits in hidden backups. Live readability remains untested. |
| Stage 4: explain decisions verbally and protect OpenFOAM time | PARTIAL | Bilingual briefs and spoken reasoning are prepared. AI has a compact 10–12 minute target. No actual timed combined talk or speaker handoff has been demonstrated; the public rule is 15–20 minutes for both tasks plus 10 minutes Q&A. |
| Stage 6: evidence-backed Q&A | PREPARED, not rehearsed | Source-linked answers cover topology, N48 versus N64, descriptor limits, individual gains, latency tails, platform differences and quality. Three rationale gaps below weaken defensibility. HPC-specific answers require the HPC owner. |
| Stage 7: final mock with clarity, reasoning and defensibility review | NOT VERIFIED / NOT RECORDED | Prepared scripts and an agent review do not constitute a timed human mock, unfamiliar-listener test, device check or member Q&A rehearsal. |

## Three remaining reasoning gaps

### 1. Slides 3–4: explain why this topology was retained

The table compares 1297, 1666 and 1912 good output tokens/s at different concurrency settings (N32, N40 and N48). The slide correctly discloses that these are not a one-factor ranking. It does not yet make the retention criterion sufficiently explicit for a listener.

State the practical criteria that are supported by retained records: fitting the 16-GPU/two-node budget, supported parallel shapes, a usable disaggregated path and latency-qualified operation with later replication. Separate these from a claim that this is globally optimal. If no common-load comparison exists, say so; do not invent one or treat three differing-load points as proof of the best topology.

### 2. Slides 5–7: explain why descriptors were a sensible first intervention

The deck now gives the concrete symptom: workers were ready, but disaggregated warmup timed out after 360 seconds before a scored benchmark. It shows request-irrelevant whole-pool descriptor construction, a request-scoped/coalesced replacement, 720 CPU range checks and the patched path reaching a complete N32 benchmark (1422.96 good output tokens/s, 95.87% joint success, zero errors).

The remaining priority argument must be explicit: source-visible setup work provided a bounded hypothesis that could be checked cheaply for range equivalence. Bandwidth, KV layout and scheduling were not measured and eliminated as competing causes in this comparison. The 403.8 million pool-source entries per rank and 188 coalesced ranges for one 4000-token request are different scoped counts, not an end-to-end speed ratio. The failing unpatched path supplies no successful scored control; descriptor-only goodput improvement and sole-cause attribution remain unknown.

### 3. Slides 8–9: connect profiling to the decode test honestly

The N48 profile identifies candidate directions; summed GPU durations are not wall-clock shares. Separate N64 first-token tails are symptoms, not a latency-component decomposition. Those limits are already well stated.

The transition still needs to explain why the supported HPC-Ops decode comparison appears next, without claiming that these kernel percentages proved it was the fix. Suggested spoken bridge:

> These profiles define candidate directions. We next show a separate controlled check of a supported decode implementation. Its benefit is established by the fresh control and repeat, not by the kernel percentages.

The matched full N60 result is 2838.85 to 2989.17 good output tokens/s (+5.30%), with higher mean TTFT (822.29 to 947.63 ms) and lower mean ITL (16.58 to 14.93 ms). Keep those tradeoffs and the separate experimental branch visible; do not retrospectively invent the original selection rationale or imply all earlier optimisations add independently.

## Required human follow-through

Run a timed combined AI/HPC mock within the official 15–20 minutes; agree the AI cutoff and HPC handoff with the HPC presenter. Ask someone who did not conduct the experiments to identify the problem, the reason for the chosen intervention and what the evidence establishes. Rehearse the three weak rationale questions above, N48/N64 representativeness, quality limits and H100/H200 attribution. Test real slideshow navigation, hidden backup access, screen sharing and microphones. Record actual duration, questions and remaining corrections afterward.

The nine late H200 runs are already reviewed in the final report but are not in this frozen deck. A concise dated appendix could support current cross-platform Q&A. The teacher does not require every run in the main talk; adding a chronological experiment list would not resolve the three reasoning gaps.

## Scope and correction

Earlier notes describing the edition as implementing the fuller feedback describe its design intent and substantial improvements. They must not be read as full teacher compliance or proof that the human mock occurred. This audit is the narrower current assessment. No slide, transcript PDF, submission ZIP, HPC payload, scheduler state or GPU budget was changed for this audit. Research remains stopped outside the already completed narrow verification stage. This review does not create evidence or authorise another GPU run.
