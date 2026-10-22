# 22 October: fresh full N62 control and the initial SLA-failure cohort

Recorded 2026-10-22T00:20:57.655133+00:00. **25365 full N62 passes** at3011.875113 good output tokens/s,
1855/1879 joint-good (98.722725%), zero errors/cancellations,687seconds. Full
60/120/30 client, exact native serving/observer payload parity against24964 and
local output/long12-case gates pass. [Sealed review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25365-20261022/REVIEW.md). The initial
squeue job-ID query was corrected after Slurm retired the completed ID; no GPU
payload or raw result changed. All raw evidence is captured with this milestone.

A new [timestamp analysis](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/phase-transition-review-20261022/REVIEW.md) checks five sealed full/short points:
all22–24 bad scored requests per point start within39ms of profiling start.
The first100ms cohort contains exactly client concurrency60/62/64. No later
joint failure or request-mean ITL breach occurs in these points. This localizes
failures but does not identify a causal hardware bottleneck. Keep every scored
request, including these failures, in the official denominator and goodput.

At unchanged elapsed time/counts, eliminating every full-run failure has only
about1.2–1.3% arithmetic gain ceiling; shorter screens magnify that cohort's
fraction. No such recovery is achieved here. Consider server-side initial burst
handling and current backend×resource split only as prospective hypotheses.
Old auto-backend P12/D4 results cannot prove the current HPC-Ops interaction.
Full N64 job25366 is already running and remains the next acceptance decision.
Official reference accuracy remains unverified; observer-off3023.072304 stays
highest accepted individual full score until new full evidence supports change.
