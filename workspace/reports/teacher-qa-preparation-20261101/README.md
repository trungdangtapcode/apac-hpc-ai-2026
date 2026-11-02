# AI presentation revision: start here

This is the study entry point for explaining how the team developed and evaluated its AI ideas. The materials describe retained experiments; they do not claim a completed human mock or invent missing original reasoning.

## Read in this order

1. [Thinking process: nine decision stories](THINKING_PROCESS_EN.md). Learn the observation, possible mechanism, expected outcome, counterhypothesis, controlled test and resulting decision. This explains why an idea was worth trying before looking at its final number.
2. [Quick spoken Q&A cards](QUICK_ANSWERS_EN.md). Practise explaining the reasoning aloud in a short answer.
3. [Detailed answers and evidence](ANSWERS_EN.md). Use the follow-up explanation, exact slide and retained source when someone asks how the conclusion was established.
4. [Vietnamese slide learning guide](../ai-final-report-20261030/TRANSCRIPT_VI.md) or [English guide](../ai-final-report-20261030/TRANSCRIPT_EN.md). Review the actual diagram, hardware, notation, colors, axes and units for each slide.
5. [Short Vietnamese talk script](../ai-final-report-20261030/TALK_SCRIPT_VI.md) or [English script](../ai-final-report-20261030/TALK_SCRIPT_EN.md). Rehearse the complete main-talk route with its transitions and HPC handoff.

## The sentence pattern to understand

> We observed ____. A possible explanation was ____. We expected changing ____ might improve ____, but it could fail because ____. We held ____ fixed and tested ____. The result supported/rejected ____; therefore we retained, repeated or closed ____.

Use a plausible mechanism to explain why the test was chosen. Use actual measurements to explain what it established. A mechanism is not automatically proven because the candidate won. If the original before-run rationale is not retained, describe the explanation as retrospective rather than pretending it was recorded at the time.

## Four reasoning chains to learn first

| Case | Why it was worth trying | What the measurements taught us |
|---|---|---|
| Request-scoped KV descriptors | Warmup failed before scoring; source built whole-pool range metadata although a request referenced only a subset. A narrow range-equivalence check could precede real serving. | CPU checks and a patched GPU run supported a usable path. No successful unpatched scored control exists, so no descriptor-only throughput percentage is established. |
| Phase-specific backend choice | A losing decode setting does not decide the prefill setting: the phases present different token shapes. A new runner/chunk can also change the context for another backend test. | DeepGEMM prefill repeated positively on H200. Later chunk/decode comparisons supported a setting-dependent improvement, not a universal library ranking or additive gains. |
| Concurrency refinement | More in-flight work might improve batching/overlap, or instead increase waiting and contention. A stronger service configuration justified bounded load tests. | N64 gained about 1.083% against the full N62 control and repeated. N68 added about 0.083% against its fresh N64 control while mean TTFT worsened; retain N64. These are different pairs. |
| H100-derived settings checked on H200 | A complete recipe port changed runner and chunk together. A loss did not identify either factor; matching the chunk tested a narrower explanation. | HPC-Ops chunk8192 recovered about 6.57% against its own 4096 branch but remained about 4.52% below the H200 incumbent. Keep the H200 recipe; do not convert H100 scores into proof. |

The detailed stories contain the job IDs, sources and scope limits. KV recovery and the later working-deployment studies are separate experimental questions, not one proven causal chain.

## Check your understanding without reading

For each case, explain:

- What was observed before choosing this test?
- Why might the change help, and why might it fail?
- What changed and what was held fixed?
- What result would have contradicted the hypothesis?
- What was learned and why did the next decision follow?
- What cause or generalisation is still unproven?

Then answer why N48 profiling does not quantify N64 latency, why GPU activity is not proof of a compute bottleneck, why 403.8 million versus 188 is not a speed ratio, and why the 90% request-latency gate is separate from the ≥99%-reference model-quality requirement. The detailed Q&A gives the evidence-backed answers.

All scores need their platform, load, control and unit. The nine H200 transfer allocations include eight N64 jobs and one N54 job, with controls for separate branches. The subsequent 28197 package acceptance is a tenth, distinct full entry run at N64; it repeats the deployment entry rather than adding a new candidate configuration. A terminal job, a complete local acceptance, a performance request-latency fraction and official model quality are different evidence classes.

These are rehearsal companions to the [current presentation](../../submission-review/ai-basic-submission-polish-20261102/TripleU_APAC2026_Presentation.pptx) and [main-talk PDF](../../submission-review/ai-basic-submission-polish-20261102/TripleU_APAC2026_Main_Talk.pdf). The final packaged-entry acceptance passed as job 28197 after a readiness-only fix to the prebenchmark failure in 28194. This closes the full post-reader-fix replay gap; it is not a matched optimisation gain. The official Qwen FP8 checkpoint is preserved for the organiser-run full-set Q1 comparison. Job 28197’s 98.6366% request-latency fraction describes serving, not answer accuracy. This companion changes no raw result or research allocation. The independent HPC owner answers OpenFOAM rank-count and variability questions. For quality policy and the exact Basic upload interpretation, see [the recorded clarification](../../notes/ai-quality-threshold-clarification-20261102.md).
