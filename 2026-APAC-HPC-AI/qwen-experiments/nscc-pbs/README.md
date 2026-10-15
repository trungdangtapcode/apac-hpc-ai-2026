# NSCC PBS alternative: Qwen commissioning

Latest completed review, 2026-10-15 19:48 UTC: **220562.pbs111 finished exit0**
after23m33s on16 H100. This is the first complete NSCC Qwen baseline:
**N32,1565.16 good tokens/s,100% SLA (966/966), mean ITL18.5724ms,
mean TTFT346.6332ms, zero errors/cancellations**, full60/120/30 protocol,
4000/200 tokens. Payload checksums pass. Output diagnostic is7/8 with only the
known reverse-string failure; H100 monolithic/long-context and organiser full-set
accuracy remain unverified. This is one H100 observation, not a repeated result
or an upper load boundary. No new PBS job was submitted; all seven own jobs
are terminal. H200 repeats23839/23859 remain PENDING(Resources), watcher alive.

All workers were healthy before the1200s deadline; PBS stdout records
prefill ready1104/1105s, decode1106s (checked after prefill), router1150s,
all pairs warm1193s and measurements complete1407s. Runtime counters separate
prefill load851.14/851.64s and graph119.07/114.96s, versus decode98.57s load
and126.82s graph. The load-time cause is not isolated. Both P/D pair requests
returned200; all16 ranks log NIXL UCX initialization. Some H100 MoE kernels
warn of fallback to older Triton tuning/no TMA; this is an inspection lead,
not a measured kernel bottleneck or a reason to change the baseline silently.
[Independent baseline review](inspection/wake-20261015-1930UTC/baseline-review.json);
[terminal raw collection](collected/220562.pbs111/20261015T194718195272Z/).

Ledger03:40:01Singapore16October still shows539.307SU used,62436.693SU
balance and1024SU In Doubt. Keep the same1024SU local reservation pending
post-completion accounting; commissioning headroom remains2532.693SU. Balance
already excludes In Doubt. Next: reconcile updated accounting, validate H100
long-context output and confirm the N32 baseline before choosing a higher load.
The historical status snapshots below retain their original timestamps.

The first full attempt220486 failed on Triton cache permissions. Private-tmp
retry220489 exited1 after10m10s at the600s prefill readiness limit. Its retained
PBS stdout shows decode weight load and CUDA graph completion with readiness
at01:12:06Singapore, while two prefill loaders continue shard progress at about
38s/shard (14/24 near timeout,15/24 during cleanup). That supports slow ongoing
load; the underlying cause has not been isolated. Extrapolated completion is
an estimate, not an observed successful startup or an OOM diagnosis.

The frozen [readiness retry](baseline-n32-readiness-02/) changes only launcher
readiness: all workers share an absolute1200s startup deadline, then router
gets120s. The16-GPU/30min allocation, private-tmp adapter, worker, official
checkpoint/client, N32 workload and full60/120/30 benchmark are preserved.
The existing benchmark refuses a point if less than240s remains; never shorten
measurement to fit. Five checks of the actual readiness function cover shared
timeout, process exit, worker/router success and router timeout; shell syntax,
frozen checksums, unchanged source files and remote asset preflight pass.
[Diagnosis, validation and submission](inspection/wake-20261015-1915UTC/).

The19:19UTC submission and accounting notes are superseded by the completed
review above. The1024SU maximum reservation remains pending ledger reconciliation.
[Budget](nscc-budget.json).

## Actual PBS tests

| Job | Outcome | Meaning |
|---|---|---|
| 220453.pbs111 | Failed before GPU test | PBS allocated two full nodes immediately; `pbsdsh` requires `--` before command options |
| 220454.pbs111 | Failed container GPU test | Host sees16 H100; raw container environment did not expose the driver library to PyTorch |
| 220456.pbs111 | Failed container GPU test | `SINGULARITYENV_*` alone did not preserve CUDA/driver variables for this raw squashfs; diagnostics show missing `libcuda.so.1` |
| **220457.pbs111** | **Exit_status0; passed** | Explicit environment after container entry works; each of two nodes completes FP16 GEMM on all eight GPUs |

The passing job ran on `a2ap-dgx023` and `a2ap-dgx025`, using driver595.71.05,
PyTorch2.5.0a0 and CUDA12.6 from the site's PyTorch24.10 squashfs. Each GPU is
H10080GB, compute capability9.0. Requested walltime was5min; PBS records46s
actual walltime. This is a tiny runtime test, not a Qwen throughput, RDMA,
NCCL, accuracy or99%-reference validation.

Original payloads and raw records for every attempt are retained in `attempts/`.
The successful [machine-readable result](attempts/04-pass/runs/220457.pbs111/summary.json)
contains all16 per-GPU GEMM checks. [PBS accounting](inspection/all-probe-accounting.txt)
retains failed attempts as failures, not completed benchmarks.

## Account, queue and budget

- Project59010042, APAC HPC-AI Competition2026 2A+42; expiry2026-11-15.
- The initial accounting snapshot reports64,000 SU granted and63,977.244 balance as of its
  reporting timestamp in the initial probe snapshot. The newer ledger below
  includes these short tests.
- NSCC charges128 SU per requested GPU-hour, with no separate CPU charge for
  GPU jobs.64,000 SU corresponds to500 GPU-hours or31.25h using all16 GPUs.
  A30-minute16-GPU request has an upper runtime cost of1024 SU. Actual ledger
  updates must be checked before a long experiment sequence.
- Submit to routing queue `normal`; our16-GPU jobs routed to `aiq2`. Direct
  submission to `aiq2` is restricted by `from_route_only=True`.
- Each full node request is normalized to8 GPUs,112 CPUs and1880GB allocated RAM.
- At the snapshot `aiq2` had no waiting jobs, and our probes started quickly.
  This does not guarantee future queue latency. Its per-user running limit is4.
- Own home quota50GB; scratch quota100TB. Model weights belong in scratch.

Primary billing reference: [NSCC ASPIRE2A+ FAQ](https://help.nscc.sg/aspire2aplus/faqs/).
Actual project/queue records: [snapshot](inspection/pbs-project-snapshot.txt).

## Prepared full benchmark, not submitted

[baseline-n32](baseline-n32/) freezes the confirmed round-robin deployment from
Firmus job23576, adapting its launcher to PBS and Singularity. It retains the
worker, official AIPerf benchmark, placement and request-scoped NIXL patch
byte-for-byte. The copied topology script changes only asset paths and the
30-minute job deadline. Source Slurm calls are handled by a narrow PBS adapter;
the three `SLURM_*` aliases preserve source artifact paths, not a Slurm scheduler.

The first H100 point is N32, P8-TP4_D8-TP8-EP8, BF16 KV, chunk4096 and dense
decode graphs1–64, with the same4000/200,60/120/30 protocol. H100 must have its
own baseline and load search; the H200 best N53 is not an H100 performance result.
The contest rules treat platform comparisons separately.

The adapter restores the OCI image environment as data, puts the host driver
libraries first, sets local GPU indices and binds deterministic CPU slices.
CPU placement is not NUMA-tuned. [CPU validation](port-validation.json) verifies
the actual adapter's GPU mapping (P0:0–3, P1:4–7, D0:0–7; CPU client: no GPUs)
and unchanged worker/client/patch. The specific SGLang/AIPerf images and NIXL
transport still require runtime validation on NSCC.

Remote workspace:
`/scratch/users/industry/ai-hpc/apacsc42/qwen-pbs-20261015`

The PBS baseline and its preflight are staged there. Before allocating GPUs:

```bash
bash ~/workspace/vpn-rootless/vpn.sh ssh "bash -lc 'cd ~/scratch/qwen-pbs-20261015 && bash submit-baseline.sh'"
```

This command **currently refuses to submit** because the required model/images
are absent. It checks assets and frozen checksums before `qsub`, so missing
files do not consume a GPU allocation. It has not submitted a full Qwen job.

## Files still needed

Destination root: `/scratch/users/industry/ai-hpc/apacsc42/qwen-assets`.

- `sglang-harbor.sqsh`: the exact Firmus server image, approximately25GB.
- `aiperf.sqsh`: the exact official-client image, approximately779MiB.
- `Qwen3-235B-A22B-Instruct-2507-FP8/`: official checkpoint,24 weight shards,
  236,426,193,880 weight bytes (220.19GiB), plus configs/index/tokenizer files.
- Canonical non-FP8 tokenizer cache: **already copied**,16MiB, under the PBS
  workspace's `hf-cache`, retaining the original AIPerf tokenizer ID.

The public checkpoint metadata is pinned to
`e156cb4efae43fbee1a1ab073f946a1377e6b969`; its shard sizes match the staged
Firmus checkpoint. Metadata only was fetched; the236GB model and both images
have **not** been transferred. NSCC login can reach the public HF metadata API.
[Asset contract](asset-contract.json), [current preflight](inspection/assets-preflight.json),
[public model metadata](inspection/official-model-metadata.json).

## Autonomous review, 2026-10-15 15:47 UTC

Staging is now in progress, superseding the original "not transferred" status
above. The existing remote downloader PID2896088 has verified official shards;
the existing local image transfer PID2861397 verified AIPerf and is transferring
the exact26.48GB SGLang image. Do not start duplicate transfers. The real remote
preflight still returns exit2: the model and server image are incomplete, so no
Qwen PBS baseline has been submitted.

The preflight now requires a completed pinned model-staging manifest, exact
official file sizes and recorded official LFS hashes, plus freshly computed
image SHA256. This closes the window where a renamed but not yet verified shard
could pass the former nonzero-size check. Five tiny CPU fixtures cover success,
incomplete verification, truncation, wrong model digest and same-size image
corruption; the frozen PBS placement/source checks also pass. The updated
preflight and image contract were copied to the remote workspace.

[Budget ledger](nscc-budget.json): latest `myprojects` reporting timestamp
2026-10-15 23:40:01 Singapore records70.543SU used,63929.457SU balance and zero
in doubt. Live own-job history has only the four terminal probes220453,220454,
220456 and220457; none pending/running. The4096SU commissioning cap conservatively
includes70.543SU already spent, leaving4025.457SU. A baseline has no reservation
yet. Before any `qsub`, refresh own jobs and credit, reconcile manual submissions,
record a1024SU reservation and preserve13000SU of project balance. The asset
wrapper checks files; it does not enforce the budget ledger automatically.

[Raw wake evidence](inspection/wake-20261015-1542UTC/),
[asset preflight validation](asset-preflight-validation.json).

After staging assets: test image imports and a real P/D request first, then run
one full N32 baseline. Only passing SLA/output diagnostics justify increasing
load. Retain H200 jobs/results until the NSCC deployment has actual valid
measurements. No automatic large sweep against the finite SU grant is enabled.

Singularity reference: [GPU libraries and visibility](https://docs.sylabs.io/guides/4.1/user-guide/gpu.html).

## Autonomous review, 2026-10-15 16:03 UTC

The pinned official checkpoint finished staging at15:54:55UTC: all33 expected
files, including24 weight shards totaling236,426,193,880 bytes, have recorded
hashes matching official LFS metadata where provided. The downloader exited
normally after its completed manifest; no duplicate was started. The live
preflight accepts the model and freshly hashes AIPerf, but still returns exit2
solely because the exact SGLang image is incomplete. At16:01:26UTC its tracked
transfer PID2861397 had16,029,483,008/26,476,240,896 bytes remotely.

Own PBS live queue is empty. Detailed history still contains only probes220453,
220454,220456 and220457.pbs111; all are terminal, with outcomes unchanged.
The refreshed project ledger as of2026-10-16 00:00:02 Singapore still reports
70.543SU used,63929.457SU balance, zero in doubt. Commissioning headroom remains
4025.457SU; no new reservation/submission. When image verification finishes,
refresh jobs/credit and record the1024SU reservation before the single N32 job.
[Preserved model, preflight, accounting and Slurm evidence](inspection/wake-20261015-1600UTC/wake-summary.json).
