# Native inference mode works by phase but does not improve useful goodput

Question: can the final two source-tested H100 phase settings improve our H200
incumbent, and can we verify activation rather than infer it from a flag?
Actual H100 effects were small, +0.2596% decode-only and -0.0114% prefill-only.
Source/context qualification under the owner's explicit transfer scope justified
one current-H200 run per arm, with a fresh explicit no_grad control. These were
intervention ports into DeepGEMM/chunk 8192/N64, not the full H100 both-HPC-Ops/
chunk 4096/N54 recipe. Do not claim four distinct winning H100 configurations.

All three jobs now complete 0:0 and replay all local raw/source/runtime/physical
KV/both-semantic-route/output gates. All use 16 H200/g1/g4/N64 and identical frozen
workers apart from phase mode exports. Exact common/scheduler hashes, native
boolean and context/restoration receipts pass for every intended serving role.
Control 27826 is False/False/False, decode-only 27828 False/False/True, prefill-only
27830 True/True/False across P0/P1/D0. The raw argument audit differs only in
engine seeds; mode is independently proven by its provider receipt, not by
ServerArgs. Role-launch preflight does not replace uncollected per-rank steady
mode/kernel traces; server inherited environment and distributed correctness
checks provide the bounded compatibility evidence actually collected.

| Job | Arm | Good tokens/s | Versus explicit control |
|---|---|---:|---:|
| 27826 | no_grad both phases |3039.167093|Reference|
| 27828 | decode-only inference_mode |3039.356215|+0.006223%|
| 27830 | prefill-only inference_mode |3043.141258|+0.130765%|

Neither clears the prospective 1% useful-gain gate. Prefill-only TTFT p95 falls
1391.127 to 1289.030 ms and sampled prefill queue means fall 1.0/0.75 to 0.3333/
0.0833, but each run still has 26 TTFT/0 ITL breaches. One observation does not
establish a robust tail benefit or causal explanation. Keep native no_grad and
the current H200 recipe; no unchanged repeat, combined-mode sweep or promotion.
Historical H200 mean 3044.400475 is a separate series, not this pair denominator.

Control 1873/1899 good (98.630858%), candidates 1876/1902 good (98.633018%) each,
zero scored errors/cancellations, smoke 7/8 non-regression, retrieval 12/12. Full
60/120/30 and requested 4000/200/seed 2026 protocol passes. Official full-set
accuracy remains UNKNOWN; local output checks are not 99%-reference certification.

Inspect beyond score: 24 five-second samples/role/16 distinct GPU UUIDs, 72 successful
metric polls per job. Decode activity 100%, running means 50.0833/50.0417/50.4583,
queue max 0, sampled VRAM 131.204/131.244/131.180 GiB/GPU and KV usage about 0.12.
No selected transport/OOM markers, Python tracebacks or failed semantic setup
responses. CPU/power/clocks/temperature distributions and full raw tail latency
were inspected. Host averages do not establish scheduler starvation; GPU active,
VRAM and KV occupancy are distinct. Missing per-thread/heavy/Xid/throttle profiles,
actual token IDs, sparse sampling and uncalibrated clocks remain limitations.

Costs: 27826 12:06 (3.226667 GPU-hours), 27828 12:16 (3.271111), 27830 11:39 (3.106667),
all 0:0; actual 9.604444 versus 13.6 maximum GPU-hours, zero PBS SU. Raw inputs,
requests, exports, frozen payloads, role telemetry and scheduler evidence are
sealed and captured; large external bytes require a separate off-host copy.

Four distinct additional source-intervention ports are now reviewed: 27804 chunk
6144, 27806 chunk 8192, 27828 decode-mode, 27830 prefill-mode. The added 27826 control
is not a fifth candidate. All four are local passes, none establishes a useful
incumbent score gain. Own queue empty in the dated final audit; the requested
verification stage is complete, not an automatic restart of broader research,
H100 authentication/spending, HPC, background Codex, schedules or published
PowerPoint/ZIP updates. The working final report receives the measured outcome.

[Complete final phase evidence](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h200-phase-inference-transfer-20261031/RESULTS.md).
