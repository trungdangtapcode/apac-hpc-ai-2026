# S62r3 Slurm submission receipt: job 26076

Submitted 2026-10-25 05:14 UTC from /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments, the parent containing the existing runs/ destination.

- Slurm job: 26076
- Partition: hpcai
- Frozen bundle: s62r3-h200-two-decode-tp4
- Allocation: two nodes, 16 H200 GPUs, maximum 17 minutes
- Experiment identity uses S62r3 and this job ID
- SHA256 manifest: all entries passed immediately before admission
- sbatch --test-only estimated 05:30:52 UTC; this is not a start guarantee
- Fresh scontrol immediately after submission: PENDING, two nodes, 8 GPUs/node
- Work directory: /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments
- Stdout/stderr: runs/26076.out and runs/26076.err under that parent; both paths verified in scheduler metadata
- Own active-job queue: one of five slots
- At 05:14 UTC, g1 was idle and g4 allocated to another team's job; queue reason was Resources
- No worker/model startup, benchmark, score or output check is claimed yet
- H200 Slurm does not consume PBS SU

This retry changes only the frozen S62r2 experiment identity and corrected fail-closed TP4 geometry validation. The previous job 26064 remains preserved as a pre-benchmark validation failure. [Preparation reasoning and 32-receipt validation](s62r3-h200-two-decode-tp4/PLAN.md).
