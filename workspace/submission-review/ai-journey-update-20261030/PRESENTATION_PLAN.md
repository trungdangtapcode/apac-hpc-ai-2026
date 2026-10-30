# AI presentation plan — 15–20 minutes

This is a proposed pacing plan for the team's stated AI allowance, not an organiser timetable. The number of speakers is not yet specified; combine the responsibilities below as needed.

## Three technical stories

1. **Request-scoped KV transfer:** what blocked deployment, how source/log evidence motivated the change, and why CPU geometry plus server readiness still did not establish useful output.
2. **Backend interaction:** how profiling motivated a controlled model trial, the matched N60 gain and independent repeat, and the limits of its causal explanation.
3. **Reproduced N64 selection:** the full N62-to-N64 pair, independent repeat, short-to-full N68 reversal and why the largest isolated score is not the selected configuration.

For each: **What happened → Why we investigated → What we changed → How we know → What remains unknown → Decision.**

## Proposed 17-minute main route

| Slides | Purpose | Target |
|---|---|---:|
| 1–5 | Result, objective, exact environment and topology | 2:00 |
| 6–8 | Transport/layout diagnosis and correctness lessons | 3:00 |
| 9–10 | Research method and overall journey | 1:00 |
| 11–14 | Backend interaction, profiling, full gain and repeats | 4:00 |
| 15 | Explain TTFT failures and measurement limits | 1:15 |
| 16–20 | H100, reversed-cost test and calibrated comparison | 2:45 |
| 21–23 | Source-guided negative trials, quality and EAGLE progression | 2:00 |
| 24 | Supported conclusion and selected configuration | 0:45 |
| 25–32 | Detailed reasoning available for questions | Backup |

Speaking target: 16:45, leaving about three minutes of buffer if the allowance is 20 minutes. Check whether the organiser includes Q&A in that allowance; this plan does not assume either arrangement.

**15-minute route:** omit standalone platform slide 4, generic method slide 9 and detailed calibration slides 19–20. State the environment with slide 5 and repeat platform/protocol/baseline at each technical result. Preserve the three technical stories and one well-analyzed failure.

**20-minute route:** use the main route, then spend remaining time on regime-recovery controls (25) or the real deployment repair (31), if useful. Avoid extending background introductions.

The unchanged HPC section remains at slides 33–40. This plan covers AI only and does not assign the HPC team's time.

## Team responsibilities

| Subject | Answer owner | Supporting responsibility |
|---|---|---|
| Architecture and transport | Speaker who rehearses story 1 | Bring up diagram or KV proof |
| Experiments and metrics | Speaker who rehearses stories 2–3 | Confirm baseline, units and source IDs |
| Runtime and profiling | Technical support member, if available | Explain collection gaps and failure boundaries |
| Timing and screen sharing | One person named before the call | Keep PDF ready and give one-minute warning |

With two people, combine architecture/runtime and experiment/metrics. With more members, assign primary and backup owners. One person answers first; a teammate adds a specific detail after an explicit handover.

## Before presenting

- Test screen sharing and microphone; open the final PPTX and PDF on the presenting machine.
- Keep EVIDENCE_CARDS.md and PANEL_QA.md ready for supporting members.
- Rehearse once with a timer and freeze one file version for everyone.
- For every result, name hardware/GPU count, deployment type, load/protocol, baseline and changed factor.
- Use “we observed,” “our hypothesis was,” and “we did not establish” deliberately.
- When evidence is missing, explain the missing measurement rather than inventing a cause or implying that another test was run.
