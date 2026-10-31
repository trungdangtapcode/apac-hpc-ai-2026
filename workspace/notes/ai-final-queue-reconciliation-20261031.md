# Final AI queue and result reconciliation

Observed **2026-10-31T09:54:58.497091+07:00**, Vietnam time (UTC+7). The owner asked whether H100/H200 are separate, whether jobs remain queued and whether any completed result was missing from final records. This is read-only checking and documentation; research remains stopped.

**Hardware:** H200 is Firmus/Slurm; H100 is NSCC ASPIRE 2A+/PBS. Keep results, controls, configurations and resource accounting separate. The selected historical H200 N64 mean is 3044.400475 good output tokens/s; H100 retained individual peak is 2433.019859 at N54, with a fresh full H100 control 2399.186728. Do not rank different configurations as a matched GPU comparison or use the local forecast ratio as a universal multiplier.

**Fresh H200 queue:** successful squeue returns zero own jobs. Fresh accounting from 29 October UTC has 13 terminal AI-worker allocations and no own allocation after 27510. Both 27506 and 27510 are completed 0:0. [Machine-readable snapshot and exact scheduler rows](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/final-status-audit-20261031/audit.json).

**H100:** the existing-path probe returns NAMESPACE_UNAVAILABLE. No authenticated PBS query is possible; current remote queue and any newer remote completed jobs remain UNKNOWN. This check starts no VPN session, login, DUO push or scheduler job. An unavailable queue is not empty; retained H100 scores are historical.

**Documentation gaps:** sparse graph 27510 and CPU prerequisite 27506 were already in the final report and packaged measured notes, but their mutable status pages and the main job ledger remained stale. Updated them and the current comparison index. Job 27510 measured 3029.861122 good output tokens/s, -0.370208% versus 27376, so dense graphs remain selected. Job 27506 is zero-GPU CPU-only: 95 seconds, JIT 26.605 seconds, two synthetic fixtures pass, native cleanup observed; it creates no inference score. Its frozen payload hashes still pass. A dedicated terminal review and original-run artifact seal now accompany it.

A hash audit corrected the initial suspicion of missing raw preservation: all four CPU raw files already had identical captured copies in final delivery cpp-cpu-27506 and the review stage. The missing items were the terminal review/canonical source-path seal and stale ledger/status, not lost raw bytes. [Coverage proof](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/final-status-audit-20261031/cpu-existing-backup-coverage.json).

No new winning result was found in this audit window; selected H200 configuration and H100 historical result stay unchanged. The dated stop note and 29 October active-job handoff are historical, superseded by this check. Earlier failures remain failures and unsubmitted drafts remain unsubmitted. No HPC worker state/budget, slide, ZIP or submission payload is changed. Capture, screen, commit and push these source/result/status corrections explicitly.
