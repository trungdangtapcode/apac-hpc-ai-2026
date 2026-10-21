# HPC/OpenFOAM research

The owner authorised this branch on 21 October 2026 while another person supports
AI. Start with the [plain-language research report](../../workspace/reports/hpc-openfoam-20261021/README.md),
then its plan, rules table and technical evidence. This tree is separate from
qwen-experiments; do not edit the other worker's serving payloads or queue.

- upstream-20261021: pinned official rules and 177 public reference files, hashes
  checked against Git blobs. These are organiser results, not our jobs.
- reference-analysis-20261021: 21 raw-log analyses, units, partition checks and
  limitations. Rebuild with python3 tools/analyze_reference.py.
- source-review-20261021: native pinned v2512 Scotch coefficient handling and GPL
  COPYING, including recorded failed path lookup.
- access-20261021: read-only endpoint facts, no authentication material.
- candidates: unsubmitted source-supported hypotheses, not measured configurations.

No team HPC result, job or reservation exists yet. The supplied endpoint accepts
SSH but has not exposed the expected Iris scheduler/kit. Recover the actual
practice and contest access, then run the valid Basic chain before tuning.
Model/mesh binaries, private keys, credentials, runtime caches and processor trees
must not enter this Git research archive or the text-only HPC submission.
