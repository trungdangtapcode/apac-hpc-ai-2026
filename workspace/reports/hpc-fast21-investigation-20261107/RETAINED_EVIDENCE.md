# Retained evidence for the 21.0859 s/step full 40-step arm

Prepared 7 November 2026. This is a bounded evidence review of already retained
Iris jobs; it submits no work and modifies no frozen run artifact. The central
question is why one complete 40-step `balanced48` arm reached **21.085907685
s/step** while the earlier arm with the same configuration took **32.001684128
s/step**.

## Exact comparison and preserved decision

The source comparison is Iris job **2295090**, a four-arm, 40-step/39-interval
BAAB replay on `iris001`: B1 balanced 48, A1 default 48, A2 default 48, B2
balanced 48. All four arms use the same 48-rank OpenFOAM workload, source,
runtime, physics, fixed-iteration settings and uncollated file handler. The
correctness, source, payload, field and force-trajectory gates passed. B1 and
B2's actual rank proofs show the **same rank-to-CPU map**, one unique CPU per
rank on IDs 0–47, with 24 ranks on each observed NUMA CPU set. Thus the 10.9158
s/step B1-to-B2 difference (34.11% lower in B2) is not explained by a changed
recorded affinity map.

| Arm | Configuration | Solver start (UTC) | Full-arm mean (s/step) | Runtime wall time |
|---|---|---|---:|---:|
| B1 | balanced48, socket/core | 2026-11-06 20:47:38.948 | 32.001684128 | 21:52.29 |
| A1 | default48 | 2026-11-06 21:10:27.400 | 24.663577539 | 17:08.26 |
| A2 | default48 | 2026-11-06 21:28:31.846 | 24.200998556 | 16:50.28 |
| B2 | balanced48, socket/core | 2026-11-06 21:46:18.187 | 21.085907685 | 14:45.00 |

The same UTC times are 7 hours later in Vietnam. Each native log has all 40
solver time rows. Existing review concludes that the pooled balanced48 mean is
26.543795906 versus 24.432288048 s/step for default48, so the candidate is
8.6423% slower pooled and is **not promoted**. The unusually fast B2 remains a
real complete arm and motivates a repeatability investigation; it is not a
matched configuration win on its own. See the [full terminal review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-balanced48-only-20261107/completed-2295090/RESULTS.md).

There is a second, distinct full-horizon warning in Iris job 2295087: the
balanced40 candidate was 40.020672136 then 22.901997128 s/step, also with the
same verified candidate CPU layout. This is supporting evidence that candidate
timing can vary sharply across repetitions, but it changes rank count and is
not a like-for-like cause analysis for the N48 job. The 2295087 candidate
remains slower pooled than its default48 controls. See its
[terminal review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-balanced40-vs48-20261107/completed-2295087/RESULTS.md).

## What the retained telemetry says

Five-second samples are present for every arm and the sampler exited
successfully. The collector reports **whole-node aggregate** scope. Its first
and last samples span 1,025, 1,010, 1,310 and 885 seconds for A1, A2, B1 and B2
respectively. The JSON produced by the accompanying script contains the
sample-by-sample summaries, first/last fifths, snapshot fields and source paths
needed to reproduce the calculations.

### CPU frequency and aggregate CPU use

Across all four arms, the median of each five-second sample's 56-CPU
`/proc/cpuinfo` median is **3,300 MHz**. Its sampled range is 2,900–4,000 MHz
for all arms. B1/A1/A2 had a median per-sample *minimum* of about 2,900 MHz;
B2's corresponding median minimum is about 3,299 MHz. This difference could be
consistent with fewer low-frequency CPUs on B2, but samples are node-level and
store only per-sample min/median/max, not a frequency keyed by the 48 rank CPU
IDs. `cpu MHz` is a sampled procfs reading, not a per-rank clock trace. It
cannot establish that B2's solver ranks ran faster because of frequency.

The external `resource-time.log` counters imply about 47.7 aggregate CPU-seconds
per elapsed second in each arm (user plus system seconds divided by wall time),
close to the 48-rank allocation for all four. This does not point to B1 simply
leaving most solver CPUs idle. It is a summed `/usr/bin/time` process-tree
counter, not per-rank utilization or a hardware counter.

### Memory, page faults, I/O and NUMA counters

In each arm the first telemetry sample saw roughly **165–166 GiB** `MemAvailable`;
within the solver interval it fell to a minimum of **39.5–41.8 GiB**. The
pre-solver and post-solver node snapshots often show about 165–167 GiB available
because they were taken outside the solver's live high-water interval. The
large drop is visible in the time series, but is not unique to slow B1: B2 has
the same approximate minimum and recovers to 166.3 GiB in its final sample.
It may reflect the job's collective working set, other activity on the shared
node, or both. The per-process maximum RSS reported by `time` is only about
2.9–3.1 GiB and is not aggregate memory for all 48 ranks. No job-cgroup total or
per-process resident-memory series was retained, so the current evidence cannot
separate those explanations. No swap-in or swap-out increments were observed.

The most conspicuous B1/B2 telemetry differences during the solver interval
are:

| Signal | B1 slow balanced48 | B2 fast balanced48 | Interpretation limit |
|---|---:|---:|---|
| Whole-node `numa_miss` delta | 150,995,241 (115,263/s) | 0 | Kernel node-wide cumulative counter; not rank- or job-attributed |
| `numa_foreign` delta | 150,995,260 (115,264/s) | 0 | Same node-wide attribution limit; nearly tracks `numa_miss` here |
| `numa_pages_migrated` delta | 254,574 (194/s) | 2,447 (2.8/s) | Node-wide counter; does not identify which process's pages moved |
| Process-tree major faults | 75,369 | 5,610 | Per timed launcher tree; could include file-backed faults, not a NUMA-residency count |
| Filesystem input counter | 66,832 | 36,712 | `time` counter as reported; cannot identify source, bytes, or responsible process |
| Kswapd scanned pages, node-wide delta | 1,640,450 (1,252/s) | 0 | Global reclaim activity; no PSI or job cgroup attribution |
| Direct reclaim scanned pages, node-wide delta | 129,014 (98/s) | 0 | Same global limitation |
| Maximum per-process RSS | 3,121,056 KiB | 3,091,960 KiB | Similar maxima; not sum across ranks |

For context, the default arms show 10.64M and 12.33M whole-node `numa_miss`
increments, respectively, while B1 shows 151.0M and B2 zero. This makes the
B1 excursion worth testing. However, vmstat values are node-global cumulative
counters, and the Iris host may have other node-level activity. They cannot
prove that B1's OpenFOAM ranks made those faults or that remote memory caused
the time penalty. The B1 higher major-fault and filesystem-input counters are
also compatible with a different file-cache / storage path, but no per-rank
I/O or cache-miss evidence says so. All arms show the same rapid `MemAvailable`
drop to around 40–50 GiB, so that broad signal alone does not explain the
opposite B1/B2 outcomes.

### Available node snapshots and explicit gaps

The retained `solver-before-node-snapshot.json` and
`solver-after-node-snapshot.json` contain `/proc/cpuinfo`, `/proc/meminfo`,
`/proc/vmstat`, collection time, and a failed `/proc/pressure/memory` read.
Those snapshots are approximately 1.3 ms to collect. Telemetry records
per-sample CPU MHz summary, aggregate CPU ticks, meminfo, selected vmstat
counters, collector timing and availability. CPU, memory and I/O PSI files
were absent. No PSI signal was collected. The snapshots and samples contain no
PID/RSS history, rank-specific frequency, process `numa_maps`, per-node process
resident pages, hardware memory bandwidth, LLC misses, per-rank page faults or
process-specific reclaim counters. Those items are **not collected**; they
must not be treated as zero.

## Light process-level evidence for the next repeats

The three exact seed48/socket-core repeats prepared by the root are a suitable
place to test whether process memory placement co-varies with the fast and slow
arms. Keep each native `mpirun ... simpleFoam -parallel` command and its frozen
input unchanged. Run a separate nonblocking observer process alongside the
solver; do not add `numactl`, `LD_PRELOAD`, a PMPI layer, profiling hooks or
extra commands to the solver launch.

At a bounded interval such as 15–30 seconds, discover the 48 live solver PIDs,
record PID and MPI rank (from the process environment when readable),
`/proc/PID/status` `Cpus_allowed_list`, and parse `/proc/PID/numa_maps` for
per-mapping policy and resident page counts (`N0=`, `N1=`, `anon=`, and file
mapping identity). Retain per-rank and per-node totals separately, with clear
warning that shared file-backed pages can be counted in multiple processes.
Capture the map once soon after all ranks appear, at several steady-state
points, and immediately before the first rank exits. Timestamp each snapshot
with monotonic and UTC time and align it to the existing solver phase markers.
If readable on Iris, sample the scheduler job cgroup's `memory.current`,
`memory.events`, and `cpu.stat` using the existing site path discovered by the
stage; retain an explicit unavailable reason if no usable job cgroup is
exposed. Do not infer a path or zero from a failed lookup.

Keep the observer low-cost: read procfs directly, avoid one `numastat` process
per MPI rank, cap its cadence, record its own elapsed time and dropped samples,
and benchmark the observer overhead separately before use. The observer should
never wait on solver progress or send signals to ranks. Compare rank-level
anonymous page placement with the already verified rank-to-CPU map. A stable
excess of remote-node anonymous pages in a slow balanced48 repeat, with no such
excess in a fast repeat, would support a locality hypothesis for a subsequent
controlled study. Similar residency in both would lower that hypothesis's
priority but would not prove bandwidth or frequency is responsible. A repeat
pattern that tracks process-specific major faults or cgroup reclaim instead
would support investigating those mechanisms. No one aggregate counter alone
identifies causality.

## Reproduction

Run the read-only summarizer with Python 3:

```sh
python3 reproduce_telemetry.py --output telemetry_summary.json
```

For another retained bundle, pass its `collected/runs/2295090`-shaped run
directory with `--result-dir`. The report's reported values are based on
`telemetry_summary.json`; source arms are under
`.../iris-balanced48-only-20261107/completed-2295090/collected/runs/2295090/arms/`.
The script does not contact Iris or change source artifacts.

