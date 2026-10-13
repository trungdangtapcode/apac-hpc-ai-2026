# Qwen experiments — updated 13/10/2026

Scope: Qwen only, official Qwen3-235B-A22B-Instruct-2507-FP8, 16 H200.

Current state: 14 original layouts and 3 separately named EP2 replacements have
been measured. Best long run: job 22415, TP4 prefill → TP8/EP8 decode, N48,
1912.30 good tokens/s and 97.44% SLA. The new serving-tuning wave is jobs
23102–23104: full-duration concurrency refinement, dense decode CUDA graphs,
and separate P/D profiling. See [current plan](serving-tuning/PLAN.md) and
[live results](SERVING_TUNING_RESULTS.md). Sections below preserve the history
of the initial sweep and its recovery; their earlier progress counts are historical.

Wave 1 finished eight jobs/twelve full measurements. Highest single point:
chunk 4096/N52, job 23114, 2140.10 good tokens/s and 98.81% SLA, pending independent
confirmation. [Wave 2](serving-tuning-02/PLAN.md) is jobs 23128–23131 for standalone
N52 controls and scheduling combinations, followed by guarded DeepEP/FP8-KV
pilots and the best two independent repeats. The shared controller limits the
account to four queued/running jobs and retains all measured/failed records.

Current expansion: [17-topology sweep results and status](TOPOLOGY_RESULTS.md),
[Vietnamese tutorial](/home/apacsc42/workspace/tutorial/09-thu-het-topology-qwen.md).
All 17 attempts ended by 2026-10-10 02:02 UTC. Eight produced measurements;
nine failed before benchmark. **The request to benchmark all 17 is NOT complete.**
The first controller stopped on terminal Slurm states instead of completed measurements.
Repair work is in `topology-repair/`; pilot job 22270 produced all four sweeps,
bringing measured original configurations to 9/17 as of 04:14 UTC. Its long
confirmation is job 22274. See [recovery progress](RECOVERY_RESULTS.md) and
[first-round review and failure classification](TOPOLOGY_REVIEW.md).
The active detached controller is `repair-topologies.py --run`, with its state,
PID, and log in `topology-repair/recovery.{json,pid,log}`. It submits missing
measurements automatically, at most 4 jobs pending/running for this account.
Do not restart the original `topology-sweep.py --run` to recover failed jobs;
that controller stopped on terminal states. Original frozen bundles and failed
run snapshots are preserved. The repair controller has its own exclusive lock.
It checks progress every 45 seconds and only counts all four actual sweep
exports with requests > 0 and no client cancellations as a completed benchmark.
Three FP8-incompatible TP8/EP1 originals remain explicitly unmeasured; their
EP2 replacements have distinct names and are counted separately.
Transport repair pilot **22294** uses a reviewable NIXL patch that creates
heterogeneous-TP transfer descriptors only for the current request. Byte ranges
match the original algorithm in 720 CPU cases; GPU validation is pending.
See [patch details and evidence](nixl-ondemand/README.md). Job 22280 was replaced
before it started; jobs 22272–22274 have an automatically resolving afterany
dependency on this pilot. Frozen payloads and failure logs remain preserved.
The new sweep uses 10/20/30 at N16/32/40/48, followed by 60/120/30 confirmation
when enough Slurm time remains. Old measurements keep their original protocol.

Read [RUNS.md](RUNS.md) for the complete job ledger, including failed attempts, observations, lessons and links to raw artifacts. Finished jobs receive `artifact-manifest.json` with SHA256/size for existing files; generated after completion, not at original submission. Raw exports preserve inputs and per-request metrics; full generated response text is not claimed to be archived. Notes live in `run-notes.json` and the watcher regenerates the ledger with `audit-runs.py`.

- baseline07: official example 4P×TP2 +2D×TP4/EP4.
- candidate09: official example 2P×TP4 +2D×TP4/EP4.
- Same SGLang/AIPerf image, KV dtype default, concurrency 16/32/64.
- Exploratory protocol: 15s warmup, 30s measurement, 30s grace; fixed 4000/200, seed2026, closed-loop, SLA3000ms/20ms.
- Official tokenizer ID Qwen/Qwen3-235B-A22B-Instruct-2507, cached offline from HF revision ac9c66cc9b46af7306746a9250f23d47083d689e; tokenizer.json hash matches the staged checkpoint.
- Exploratory measurements, not official scores or quality verification.
- Each deployment includes a few gateway connection-warmup requests, not benchmark prompts.
- Scripts snapshot configuration; logs/exports per job and concurrency in runs/.
- No OpenFOAM jobs.

Job 22130 failed before measurements: AIPerf offline loader tried treating a local tokenizer path as a Hugging Face repo ID. Fixed with canonical official tokenizer ID and staged HF cache. Candidate job 22131 and baseline rerun 22135 use the fixed client. Failure logs are preserved; 22130 is not a performance result.

Each job also performs 60s warmup /120s measurement /30s grace on its highest-goodput passing sweep point. This confirms the local exploratory result; dataset uses cached official tokenizer ID and artifacts flag, and is not a submission to BTC or an accuracy check.

Update: baseline sweep job 22135 had no passing point, so its automatic confirmation was skipped. Its initial measurements still encountered cold KV paths (N16 also cancelled 14 requests at grace timeout). Job **22143**, `baseline07-full.sbatch`, explicitly warms all 8 P/D pairs using temporary single-pair gateways and one short non-benchmark request per pair, then measures **N32 with 60/120/30**. It keeps the same workers/model/backend as baseline07. Pair gateways are stopped before the benchmark. See `warm-pairs.sh`, pair-warmup.log and per-pair router logs. No benchmark dataset or official seed is used for connection setup.

Read [RESULTS.md](RESULTS.md) for the Vietnamese comparison. Only canonical measurement exports are summarized; warmup exports and profiling duplicates are excluded. Client cancellations are recorded separately from the raw export's good_request_fraction.

Job 22143 failed before benchmark because all temporary gateways and the main gateway used the default Prometheus port 29000. API ports were distinct but metrics ports were not. Fixed `warm-pairs.sh` with distinct `--prometheus-port` values 29110–29117; validated all eight argument sets using the router parser extracted from the actual image. The corrected baseline confirmation is **job 22147**. Failed job snapshots are preserved.

`watch-results.py` runs as a separate CPU process on login. It checks only our five job IDs every 30 seconds, updates `job-status.json`, `comparison.json`, `RESULTS.md` and the research experiment CSV, then exits once these jobs are terminal. It submits no jobs. Its log is `watch-results.log`; rerun manually with `python3 watch-results.py` if needed. Reopen the Markdown file to see updated results.

Job 22147 failed before benchmark: gateway /health succeeded before async worker registration; warmup got a no-prefill-workers HTTP 503. Added bounded retries only for explicit no-worker 503 responses, and checked this race with mocked HTTP responses for all 8 pairs on CPU. Job **22197** is the corrected confirmation. It is not a new topology or performance result yet.

Baseline confirmation 22197 completed: N32, 809/832 good requests, 1297.02 good tokens/s. 09/N32 measured 1472.73 (+13.55% in these two full runs; repeated A/B still needed). Next job **22200** uses `candidate09-fine.sbatch`: same topology09 and images, explicit 4-pair connection warmup, sweep N40/N48, then 60/120/30 confirmation on its best passing point. No KV/kernel/backend changes.
