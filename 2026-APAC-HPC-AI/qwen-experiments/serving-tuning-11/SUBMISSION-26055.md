# S62 Slurm submission receipt: job 26055

Submitted 2026-10-25 03:04:07 UTC from frozen bundle `s62-h200-two-decode-tp4`.

- Slurm job: `26055`
- Partition: `hpcai`
- Request: two nodes, 16 H200 GPUs, maximum 17 minutes
- Frozen command: `serving-tuning-11/s62-h200-two-decode-tp4/job.sbatch`
- State immediately after admission: `PENDING (Resources)`, zero elapsed, no node assigned
- Queue before admission: no apacsc42 jobs; both H200 nodes were occupied. The test-only estimate was 03:19:32 UTC and is not a start guarantee.
- PBS SU: none; this is an H200 Slurm allocation.
- Payload: `s62-h200-two-decode-tp4/SHA256SUMS`, verified before submission; all entries passed.

No worker startup, AIPerf measurement, output check or score exists yet. Do not count the queued attempt as a completed benchmark. Preserve this receipt independently of the frozen payload.

## Pre-start cancellation and warmup-capacity correction

At 03:06:19 UTC the job was still `PENDING (Resources)` with no node assigned. The frozen runner had an absolute 120-second warmup budget and only two warmup threads for four P/D routes. Historical job 22219's same 2×2 topology took up to 150.55 seconds to initialize all four routes. That made a pre-benchmark timeout plausible and the 120-second cap insufficiently justified. Job 26055 was cancelled at 03:06 UTC before allocation: `CANCELLED+`, exit 0:0, elapsed 0, no node. It consumed no GPU allocation time and has no benchmark result. A corrected immutable revision will raise the route fanout to four and the warmup budget to 180 seconds before resubmission.
