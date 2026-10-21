# 21 October: accepted short load gain proceeds to full matched confirmation

Recorded 2026-10-21T23:55:57.519836+00:00. All five previously queued H200 jobs are now COMPLETED/0:0;
the fresh 23:51 UTC queue is empty. Earlier pending snapshots are historical.
[25339 sealed short review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-review-25339-20261021/REVIEW.md) validates 608/632 good requests at N62
and 627/649 at N64, zero errors, matching short protocol and long 12/12. Scores
2811.316116 and 2891.760212 good output tokens/s imply a 2.861439% within-job gain,
exceeding the prospective 1% screen gate. Actual exported token lengths include
one199 record at N62, similar to accepted full controls. A strict offline200-only
assertion was corrected; fixed request settings are not a per-response ID proof.

Question: does the gain survive full 60/120/30 measurement after fresh startups?
[New full plan](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/research-followup-20261021-n64-full/PLAN.md) freezes equally observed N62 control and N64 candidate
from the same native full recipe, with identical operational files and only
concurrency changed. Each requests 16 H200 / two nodes / max17 minutes, no PBS SU.
The source graph range is 1..64. Submit under the shared queue lock/cap5 after
actual partition and immutable checksum checks; candidate follows afterok control.

No short-score promotion: observer-off full24962=3023.072304 remains incumbent.
The other four full N60 reviews close losing both-HPC8192 and power_of_two router
branches, while worker-locality capture changes score by only 0.1375%; these are
not replacements for the distinct N64 load hypothesis. Full organiser accuracy
remains unverified. Retain raw failures, telemetry gaps and all source evidence.
