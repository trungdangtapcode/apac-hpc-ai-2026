# Explain decisions through four research questions

The owner rejected chronology as the main argument. Use the seven-step framework supplied by the owner inside four research questions. Research is stopped; this is a reporting change. Preserve English slide content, the existing theme, 32 AI slides and eight independent HPC slides. The Vietnamese transcript remains the requested exception.

## Scientific discipline

A failure stage or large source operation count motivates a hypothesis; it does not prove the dominant end-to-end bottleneck. Keep measured facts, hypotheses, decisions and missing attribution distinct. For KV transfer, 22271 timed out before scoring and 22294 completed a full benchmark; no successful unpatched control isolates descriptor-only speedup. CPU range equivalence is separate from real GPU validation.

## Main route

- Slides 2–5: How should we distribute prefill and decode across 16 H200 GPUs?
- Slides 6–7: What limits the performance of the selected deployment?
- Slides 8–13: Which interventions improve goodput without violating the SLA?
- Slides 14–18: Are the improvements reproducible and robust?

Slides 1 and 19–20 frame the questions, answer them with evidence boundaries, and state proposed validation. Slides 21–32 hold the chronological milestones, topology compatibility, detailed KV repair, H100 trials and other supporting evidence. The eight HPC slides remain untouched. Target 17–18 minutes for AI, compressing backup material into Q&A.

## Owner-supplied reasoning chain

Problem & constraints → Baseline & observation → Bottleneck analysis → Prioritisation & hypothesis → Intervention & measurement → Evidence & causal analysis → Conclusion & next iteration

## Slide map

| Slide | Research role | Proposed title | Hardware |
|---|---|---|---|
| 1 | RQ1–4 · Problem & constraints | How do we reason about a fast Qwen service? | H200 + H100 |
| 2 | RQ1 · Problem & constraints | Define success before choosing an optimisation | H200 primary · H100 separate |
| 3 | RQ1 · Baseline & observation | Which GPU layouts are feasible candidates? | 16 H200 · Firmus |
| 4 | RQ1 · Conclusion from topology evidence | Why keep two TP4 prefills and one TP8 decode? | 16 H200 · Firmus |
| 5 | RQ1 · Observation → validity check | Worker readiness did not prove a working service | H200 · hetero-TP recovery branch |
| 6 | RQ2 · Bottleneck analysis | What does the profile identify—and what does it not? | H200 · N48 diagnostic |
| 7 | RQ2 · Prioritisation & hypothesis | Why investigate descriptor setup before bandwidth? | H200 branch · CPU/source diagnostics |
| 8 | RQ3 · Hypothesis → intervention | Do attention and communication choices interact? | H200 · N52 |
| 9 | RQ3 · Matched measurement → causal limits | Does a decode change improve the service objective? | H200 · full N60 |
| 10 | RQ3 · Intervention & full measurement | Where should we stop increasing concurrency? | H200 · N62 → N64 |
| 11 | RQ3 · Evidence & unresolved cause | Which requests still fail after goodput improves? | H200 · N64 · job 26766 |
| 12 | RQ3 · Evidence → keep or reject | Keep an intervention only if the objective improves | H200 results + separate H100 FA3 pair |
| 13 | RQ3 · Failed hypothesis → revised test | Did speculative decoding solve this workload? | H200 · EAGLE3 |
| 14 | RQ4 · Reproducibility & selection | Does the improvement survive another deployment? | H200 · full N64 repeats |
| 15 | RQ4 · Robustness & confounder checks | Why did a later replay score lower? | H200 · distinct runtime series |
| 16 | RQ4 · Frozen forecast → held-out evidence | Can one platform predict another reliably? | H100 inputs · H200 verification |
| 17 | RQ4 · Quality boundary | What does passing latency leave unverified? | H200 latency · official quality unknown |
| 18 | RQ4 · Real replay & failure analysis | Does the packaged deployment complete end to end? | H200 replay + CPU reader verification |
| 19 | Conclusion · Answer the research questions | Four decisions, each with an evidence boundary | H200 primary · H100 separate |
| 20 | Conclusion & next iteration | What should the next iteration establish? | Proposed validation · no new jobs |
| 21 | Backup · Environment | Backup · two platforms, separate experimental systems | H200 + H100 |
| 22 | Backup · Compatibility mechanism | Backup · FP8 geometry constrains a topology | H200 · tested FP8 path |
| 23 | Backup · Chronology as supporting evidence | Backup · historical milestones behind the decisions | H200 · different loads and runtimes |
| 24 | Backup · Intervention & correctness | Backup · request-scoped descriptor construction | H200 branch · CPU geometry |
| 25 | Backup · End-to-end evidence & limits | Backup · what the KV recovery run actually proves | H200 · jobs 22271 / 22294 |
| 26 | Backup · Platform-specific tradeoff | Backup · H100: first-token gain, goodput loss | H100 · NSCC · full N54 |
| 27 | Backup · Cost hypothesis & confirmation | Backup · does a startup saving survive reversed order? | H100 · NSCC |
| 28 | Backup · Negative measured interventions | Backup · source-supported changes that did not win | H200 · full-model comparisons |
| 29 | Backup · Diagnostics versus full serving | Backup · scope limits of kernel and source evidence | H200 + H100 + CPU · separate rows |
| 30 | Backup · Exact deployment settings | Backup · the retained settings on each platform | H200 N64 + H100 N54 |
| 31 | Backup · Fixed protocol & negative result | Backup · workload control and prefill chunk trial | H200 chunk trial · shared workload rules |
| 32 | Backup · Resource metric versus objective | Backup · less graph memory did not raise goodput | H200 · sparse graph trial |
