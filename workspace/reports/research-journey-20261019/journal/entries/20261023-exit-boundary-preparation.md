# Observe the exit boundary before another full serving repair

23 October 2026; preparation only. Question: why does 224116 report F/exit1 when real byte checks and component success markers pass? Prior evidence narrows the issue but cannot identify whether Python process teardown, the container, node cleanup or PBS staging fails.

Keep native transfer code, source hashes, full region geometry and byte gates unchanged. Add a supervisor that waits for the native Python child to finish and records its actual return and timeout status. The node shell separately records container and cleanup returns; the batch EXIT trap records its final status. An independent head gate requires source-bound, matching, complete zero-exit records. Scheduler stageout remains a separate terminal observation.

Tests use real stdlib child processes with exit 0, exit 17 and timeout, malformed/missing receipts and the actual node shell with mocked container exits. The original five native sparse fixtures, syntax and checksums pass. These tests do not exercise a GPU, real Singularity or PBS. No lifetime or transport behavior fix is claimed; the original failure's cause remains unknown.

One separately frozen two-H100/two-host ten-minute diagnostic may reserve at most 42.666667 SU under the unchanged budget. The prior 42.666667 SU maximum remains reserved pending unique posting; current internal headroom 4507.703333 SU can cover the new maximum. No reservation or qsub exists at this preparation checkpoint. Preserve H200 25682 unchanged.

A successful diagnostic establishes observed process completion, not model output or speedup. A failure with a new receipt can localize the next boundary; missing evidence remains uncertainty. Do not repeat unchanged without new information. [Exact design, fixtures and frozen manifest](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nixl-exit-boundary-probe-20261023/PLAN.md).

For a presentation: “A function can finish its calculations before the surrounding program finishes shutting down. We now record the exit of each layer separately so a success message cannot conceal a later process failure.”
