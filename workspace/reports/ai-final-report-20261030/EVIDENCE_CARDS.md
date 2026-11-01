# Evidence cards for the AI engineering investigation

| Story | Question and evidence | Supported decision | Limit | Slides |
|---|---|---|---|---|
| Choose a usable 16-GPU layout | 17 usable topology observations; later repeated N64 H200 service | Retain two TP4/EP1 prefill workers plus one TP8/EP8 decode worker for the measured system | Loads and history differ; no matched ranking of every feasible topology or global optimum | 3–4; backups 17–19, 26 |
| Repair one transfer setup path | 22271 warmup timed out before scoring; source shows whole-pool descriptor work; 720 CPU range checks; patched 22294 warmup and N32 serving | The request-scoped patch made this path usable in the measured run | No successful unpatched scored control, isolated old/new timer or proof descriptors dominate bandwidth/layout/scheduling | 5–7; backups 20–21 |
| Test a decode implementation | Matched full N60 control/treatment: 2,838.853→2,989.175 good tokens/s (+5.295%); TTFT 822.292→947.627 ms; ITL 16.579→14.934 ms; repeat −0.033% | Keep as a supported tested implementation choice with explicit TTFT tradeoff | Separate from N48 diagnostic; not an isolated kernel-time cause or additive speedup | 8–10; backups 22–25, 27–28, 30, 32 |
| Select service load and check tails | Full N62/N64 pair +1.083%; independent N64 repeat; full N68 +0.083%; N64 request scatter 1,875/1,902 pass | Retain N64 under the team's useful-gain rule | Request scatter identifies TTFT failures, not their internal cause | 11–13; backups 29, 31 |
| Port H100-derived ideas to H200 | Nine reviewed H200 jobs: fresh control 27777 3,038.023; full H100 recipe N64 27783 2,721.816; chunks 27804/27806 2,821.885/2,900.607; phase modes 27828/27830 +0.006%/+0.131% against explicit control 27826 | None passes the prospective 1% useful-gain gate; retain DeepGEMM/chunk8192 prefill and HPC-Ops/FlashInfer/MNNVL decode at N64 | Ports are not four full H100 recipe reproductions; all scores are H200. No universal cross-GPU conversion or quality certification | 14, 16; backup 34 |

## Latest transfer decision

The final wave comprised jobs 27777, 27779, 27781, 27783, 27804, 27806, 27826, 27828 and 27830. All nine completed with the team's full local checks. The four distinct source-intervention ports were 27804, 27806, 27828 and 27830; 27826 is their explicit control. The older H100 forecast remains backup 33. The new measurements do not replace the H200 incumbent. Full organiser model quality is still UNKNOWN.

Sources: [four-job transfer](../../../2026-APAC-HPC-AI/qwen-experiments/h200-h100-transfer-review-20261031/FINAL_RESULTS.md), [chunk variants](../../../2026-APAC-HPC-AI/qwen-experiments/h200-hpc-chunk-transfer-20261031/RESULTS.md), [phase-mode ports](../../../2026-APAC-HPC-AI/qwen-experiments/h200-phase-inference-transfer-20261031/RESULTS.md), [nine-run integrity coverage](../../../2026-APAC-HPC-AI/qwen-experiments/h200-integrity-check-20261101/README.md).
