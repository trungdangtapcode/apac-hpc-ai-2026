# Final entry failed before benchmark: 28194

Reviewed 2026-11-02T07:56:22.615457+07:00, Vietnam time (UTC+7). Top allocation FAILED/22:0 after 334 seconds; child cleanup is terminal and the own-user queue no longer contains the job. Top-level elapsed accounting: 1.484444 GPU-hours, zero PBS SU; maximum reservation retired once. No benchmark score or quality result exists.

All three workers passed health/readiness. Router logs explicitly report background worker initialisation, zero healthy workers, /health200 then /v1/models503. The one-shot curl exits22 under set-e before ALL_WORKERS_READY, semantic warmups or AIPerf. This is a real startup-readiness race in the submitted entry, not an inference, reader or quality result.

Preserve failed bytes and output. Derive a bounded model-list readiness gate that checks valid JSON with qwen, process liveness and the original job-start+600-second deadline. Retain later semantic gates and the entire official command. A narrow corrected acceptance attempt continues the owner's requested final-validation objective; it is not a blind retry or optimisation restart. The published ZIP remains unchanged until a corrected entry is qualified and deliberately published.

The first local cleanup check queried the retired job ID, which can return Invalid job id. The corrected own-user queue check plus terminal sacct establishes retirement; no extra GPU job was submitted by that check.
