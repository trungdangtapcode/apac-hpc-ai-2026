## AI research at a glance

**419 retained allocation IDs · 406 confirmed starts · 31 research milestones.** The history includes successful runs, failed attempts, rejected ideas, controls and the final accuracy check. Snapshot: 3 November 2026.

| Platform | Confirmed started | Cancelled before start | Start unknown | Recorded IDs |
|---|---:|---:|---:|---:|
| 🟢 H200 · Firmus / Slurm | **284** | 11 | 0 | 295 |
| 🔴 H100 · NSCC / PBS | **122** | 1 | 1 | 124 |
| **Total** | **406** | **12** | **1** | **419** |

Counts refer to scheduler allocations, including probes and failures; one allocation may contain several benchmark points. H200 includes the original HelloGPU lesson. [Count definitions and evidence](workspace/reports/ai-run-lineage-20261103/README.md#how-many-times-did-we-run).

[![Qwen research lineage: H100 in red, H200 in green, chronological milestones and documented relationships](workspace/reports/ai-run-lineage-20261103/journey.png)](workspace/reports/ai-run-lineage-20261103/journey.svg)

**Click the diagram to zoom.** Green identifies H200; red identifies H100. Solid arrows show documented derivation, dashed arrows identify controls, and dotted arrows show which finding motivated the next question. The overview groups 31 technical milestones; the complete inventory contains all 419 job IDs, including different concurrency settings.

| What the investigation established | Retained result |
|---|---|
| A repeatable H200 serving operating point | Historical N64 three-run mean: **3,044.400475 good output tokens/s** |
| A complete portable deployment | Job **28197**: **3,051.518173 good output tokens/s**, **98.636602%** joint latency pass share; a separate acceptance run, not a matched optimisation gain |
| A complete answer-quality comparison on the same 16 H200 | Stock FP8 **9,460/12,032** correct; optimised service **9,452/12,032**; **99.915433% accuracy retention**, passing the team's local 99% gate |

The H100 and H200 performance series remain separate. The local MMLU-Pro result is distinct from organiser quality certification. [Full quality method and result](workspace/reports/ai-quality-verification-20261103/FULL_RESULTS.md).

**Explore the data:** [research guide](workspace/reports/ai-run-lineage-20261103/README.md) · [all 419 nodes](workspace/reports/ai-run-lineage-20261103/all-allocations.svg) · [PDF map](workspace/reports/ai-run-lineage-20261103/journey.pdf) · [CSV inventory](workspace/reports/ai-run-lineage-20261103/runs.csv).

**[Open the interactive research atlas ↗](https://trungdangtapcode.github.io/apac-hpc-ai-2026/)** — explore **31 milestones / all 419 jobs** with pan/zoom, search, platform filters and evidence details. Hover shows **good output tokens/s · mean TTFT (ms) · mean ITL (ms) · SLA pass (%)**; missing values are N/A. [Offline copy](workspace/reports/ai-run-lineage-20261103/index.html.gz): decompress and open in a browser. The hosted viewer is the retained 3 November snapshot, not a live queue.