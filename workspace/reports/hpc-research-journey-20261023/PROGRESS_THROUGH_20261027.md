# Can the NSCC mean step fall below 3.36 seconds?

Written 2026-10-27T07:49:52.309535+00:00. This is a retrospective explanation from retained evidence, not a new optimization result or an official score. The retained best reviewed full NSCC run remains **3.364622070 seconds per step**.

## Why a lower result is plausible

The organisers' retained ASPIRE-2A CPU reference `nosrx-scotch-4node` records **3.210832548 seconds/step**, using four nodes, 512 ranks, 150 solver steps and 149 timed samples. Our reference replay found solver End, no Signal 7 or unexpected fatal marker, and final Cd **0.283983007632**, matching our Scotch repeat's final Cd. This is a retained organiser log, not our run and not complete scheduler-level proof of a clean end-to-end organiser job. It demonstrates an observed timing below 3.36 on the same named platform; it does not prove we can reproduce that speed on any allocation.

Reaching that observation would reduce our mean by approximately **4.57%**. It is a useful comparison point, not a predicted gain or a measured lower bound. Still lower reference timings include teardown faults, so this explanation uses the reference without that solver-log fault rather than treating all low values as equally qualified. Gadi and Iris timings do not establish a target for NSCC.

[All organiser reference results](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/reference-analysis-20261021/RESULTS.md). Source identity: `upstream-20261021/sources/4.3-aspire2a-logs/nosrx-scotch-4node/50_simpleFoam.2026-10-07_10-11-20.log`, SHA-256 `8287e5b6d02f37f32db887a964fe1002d5c7603a8516486dc0bdce65bc048a99`.

## What changed during our journey

| Stage | What was tested | Observation | What it supports |
|---|---|---|---|
| 21 October, first native NSCC baseline | One node, 128 ranks, hierarchical, 40 steps; job 25905114 | 14.921981 s/step | Successful workload baseline. This is not comparable to four-node timing as a software speedup. |
| 21 October, same-node method pair | Hierarchical versus default Scotch, job 25907325 | 14.787224 versus 14.640233 s/step | Scotch 0.994% lower in one ordered short pair; repeatability not established. |
| 21 October, NUMA-aware partition hypothesis | Default versus topology-aware Scotch, job 25907753 | 13.880988 versus 14.358715 s/step | Candidate lost by 3.44%; a smaller graph cut did not guarantee a faster solve. |
| Four-node screen, reviewed 23 October | Hierarchical and Scotch, each at 64/96/128 ranks per node | At 128 ranks/node: 3.819929 versus 3.677907 s/step | Default Scotch128 was the lowest observed mean in the six-run screen. Separate allocations and missing terminal evidence limit causal and scoring claims. |
| Independent confirmation, reviewed 24 October | Same intended default-Scotch128 configuration, four nodes, 150 steps; job 25940700 | **3.364622 s/step** | Stronger source, work, timing, output and terminal evidence. It is replication, not a new algorithm. |
| 24–27 October, placement diagnostics | Inspect affinity before/after MPI; test post-initialization main-thread pinning, job 26016270 | All 512 native main-thread targets qualify | The mechanism works in the probe; full OpenFOAM solver benefit remains unmeasured. |

The lower-rank four-node Scotch runs measured 10.309944 s/step at 64 ranks/node and 7.146019 at 96, compared with 3.677907 at 128 in that screen. The corresponding hierarchical observations were 4.488921, 4.922348 and 3.819929. These were separate allocations, not matched causal trials. We do not recommend reducing ranks on the strength of a theoretical communication benefit while ignoring those losses.

The earlier [journey](JOURNEY.md) explains access, preparation, density and failed graph branches. The [six-run review](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/four-node-review-20261023/RESULTS.md) preserves every result and its limitations.

## Why 3.68 to 3.36 is not an 8.52% tuning claim

The original Scotch512 observation had a 35.883552-second slow step; the repeat's maximum was 5.900974 seconds. The untrimmed mean fell **8.52%**, while median fell only **0.51%**, from 3.298742 to 3.282043 seconds. The repeat's p95 actually rose from 3.795740 to 3.936923 seconds. No samples were deleted. The distribution changed between allocations, and the logs alone do not establish its cause.

Our defensible achievement is identifying a promising conventional configuration, rejecting losing branches and producing a much better qualified full-run reference. We have not yet demonstrated a repeatable matched four-node optimization beyond that reference. [Independent confirmation and evidence](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/completed-review-20261024/RESULTS.md).

## What to test next and how to judge it

First qualify post-MPI main-thread pinning through the actual OpenFOAM Pstream path. A native probe alone does not prove the interposer is compatible with OpenFOAM. Integration job **26019383** was submitted for that purpose; a fresh PBS history listing at approximately **07:48 UTC on 27 October** shows **F**, but no exit status or completed-artifact replay was obtained in this explanatory turn. F means terminal, not success. Do not call the integration gate passed. Its payload is frozen.

If that gate passes, prepare native-versus-identity-pin **A–B–B–A** runs with unchanged Scotch partition, exact initialized input copies and the full 150-step work in each arm. Check actual mapping, all timing samples, tails, Cd, fixed iteration counts and exits. Consistent improvement across the matched arms is more convincing than one newly low mean. Main-thread affinity does not prove helper-thread affinity, NUMA page placement or a hardware bottleneck.

Only after that qualification should a new controlled branch change rank grouping or placement to reduce communication. Earlier graph-cut improvements are hypotheses, not measured traffic savings. Any transport variant also needs separate correctness and exit checks; retained alternatives are not an unexplored discovery merely because their organiser timing is lower.

There is no defensible current estimate that promises 3.0 or 2.0 seconds/step. Around 3.21 is an observed platform reference to attempt to reproduce, not an assertion that 3.21 is the hardware limit.

## Operational boundary of this explanation

A read-only CPU scheduler query also showed queued jobs 26023372, 26023373, 26023382 and 26023383 at approximately 07:48 UTC. Their provenance and payloads were not inspected here; the shared account alone does not identify the submitter. No queue, reservation, submitted payload, other worker's work or submission material was changed. This report does not override the existing admission caps or imply spare capacity for another job. It records the historical findings and next scientific gate.
