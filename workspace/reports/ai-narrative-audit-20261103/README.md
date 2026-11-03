# Does the current AI talk meet the teacher's narrative feedback?

Reviewed 3 November 2026 against `/home/apacsc42/requirement.md`, the live combined PowerPoint, the retained AI source texts and bilingual scripts. This is an assessment, not a new slide publication.

## Verdict

**The talk follows the requested reasoning substantially, but it is not yet as selective and self-explanatory as the feedback calls for.** The research archive should retain all experiments; the main talk should select the observations needed to explain two or three decisions. Neither 419 job IDs nor the complete lineage graph belongs in the main presentation merely because it exists.

The actual combined deck has 42 slides. Its current hash differs from the earlier AI publication because the combined presentation has since changed; all 34 AI slides' visible texts still exactly match the retained AI source. This audit does not modify or certify the separate HPC worker's updated content.

## What already works

| Main slides | Reasoning supported by the current material |
|---|---|
| 1–4 | Define latency-qualified service under sixteen GPUs, distinguish claim types, apply feasibility/compatibility gates and show the retained architecture. The topology observations are explicitly not a common-load global ranking. |
| 5–7 | Workers were ready but warmup failed; source inspection exposed request-independent metadata work; byte-range equivalence was cheap to check; a patched distributed request then became usable. The successful run supports feasibility, not an isolated descriptor speedup. |
| 8–10 | Profiles identify candidate areas with limits. A separately justified supported backend is tested against a matched control; goodput rises while TTFT worsens and ITL improves. The tradeoff leads to a choice, with replication rather than an isolated peak. |
| 11–13 | A short-load signal is tested with the full protocol, N64 repeats, N68 does not sustain a useful improvement, and the portable entry is independently accepted. |
| 14–16 | Test transferability directly on H200, retain losing alternatives, then measure complete answer quality against a stock reference rather than inferring it from unchanged weights. |

These are meaningful improvements over a chronological list of experiments. Teacher-requested claim distinctions and uncertainty are present. They do not, however, guarantee that an audience can follow the logic without the speaker explaining the links.

## Priority improvements before calling the presentation finished

1. **Make the decision spine audible and visible.** Use three connected questions: Can we make the split deployment work? Which change increases qualifying service output? Does the retained choice survive full repeats, packaging and quality checks? Each section should end with the resulting engineering decision, then state why the next question follows. Current slides 13–16 can feel like a checklist of independent results.
2. **Keep only decision-bearing numbers in the main talk.** The KV case needs a setup failure, a request-scoped change, its correctness check and real serving feasibility. The backend case needs the matched improvement plus the latency tradeoff. Robustness needs a repeat, the retained recipe and a compact quality comparison. Detailed job ledgers, extra decimal places, secondary ports and the complete history belong in Q&A/report materials. The new quality slide is accurate, but as the final AI slide it currently closes on a score more than the overall engineering lesson.
3. **Explain why the particular intervention was chosen.** The scripts explain why request-scoped metadata was a narrow, cheaply falsifiable hypothesis. The visible profile/backend bridge is weaker: the N48 profile did not identify HPC-Ops as the uniquely justified remedy. Present supported decode implementation as a practical controlled probe; do not imply a causal bottleneck diagnosis from kernel percentages.

## Concrete defects found in this audit

### Slide 3: topology label and measured point do not agree

The displayed `09 · N40 · 1666.01` attribution is inaccurate. `qwen-experiments/TOPOLOGY_RESULTS.md` records the earlier topology 09 job **22200 at 1649.27 good tokens/s**. The **1666.01** point belongs to separate job **22219**, layout `P8-TP4_D8-TP4-EP4`. The later lineage audit already distinguishes them. Correct the slide's label/point against the source before presenting; do not reuse the current combination as evidence for topology 09. This correction has not been published by this assessment.

### Slide 14 brief: “Every candidate stayed below” contradicts the phase-mode observations

The English brief says every candidate stayed below the fresh H200 control, then notes positive phase-mode changes. The defensible conclusion is: **none of the tested transfers cleared the prospective 1% useful-improvement threshold**. Some settings lost, while phase-mode points were slightly positive against their own separate control. This brief needs correction; the claim is not “all scores were lower.”

### Evidence limits and rehearsal remain necessary

The quality check is a complete local MMLU-Pro pass, not organiser certification or proof of identical outputs. N48 profiling does not establish N64 per-request causal timing. The KV recovery lacks a successful scored unpatched control. These distinctions should be explained briefly where they affect a decision, with detailed defence in the appendix.

A human timed combined mock presentation is still not established by file-generation or checksum tests. The speaker should be able to explain each principal case as **observation → testable expectation → controlled change → result → decision**, without reading the entire table. Preserve the agreed HPC speaking allocation.

## Recommended spoken spine

> We first needed a feasible split deployment within sixteen GPUs. A warmup failure exposed a narrow setup hypothesis that we could check cheaply, and a real run established that the patched path worked. Once the service was usable, we tested supported execution choices with matched controls and kept a measured throughput/latency tradeoff. We then increased load only while full tests and repeats supported it. Finally, we checked that the packaged service worked and that the complete deployment retained answer accuracy against a stock reference. The resulting configuration is defensible within these tests; the investigation does not prove a universal optimum.

The first sentence about the KV branch must remain explicitly scoped: it was a particular heterogeneous-TP recovery branch, not proof that this patch created every later performance increase.

## Preservation and next decision

Retain this assessment with the research notes. No GPU run, slide/ZIP publication or HPC modification is performed here. A subsequent narrative revision should make the three decision stories easier to follow, correct the two concrete defects, regenerate matching scripts and PDFs, and preserve exact measurement provenance rather than add more benchmark numbers.
