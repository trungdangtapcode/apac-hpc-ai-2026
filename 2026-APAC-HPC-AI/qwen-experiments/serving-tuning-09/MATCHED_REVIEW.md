# Wave9 matched review — 2026-10-15 21:51 UTC

Historical preflight: all three jobs were PENDING(Resources) at21:50:29UTC. This was CPU preparation,
not a new benchmark. Own Slurm stored batch scripts23904–23906 exactly match the
frozen job.sbatch files. Registry payload hashes and SHA256SUMS pass for each
bundle. Relative to23778, all common scripts match; worker differences are
exactly the one named factor. No queued payload or watcher was changed.

| Job | Single worker change | Good tokens/s | SLA | TTFT mean ms | ITL mean ms |
|---|---|---:|---:|---:|---:|
| 23778 | MNNVL, chunk4096 baseline | 2592.1624 | 99.0068% | 516.2843 | 17.1273 |
| 23839 | independent identical baseline | 2592.9236 | 99.0074% | 508.2482 | 17.1545 |
| 23904 | add FlashInfer decode attention | 2631.0854 | 99.0220% | 635.2331 | 16.2334 |
| 23905 | prefill chunk2048 | 2331.3530 | 98.7697% | 1188.7699 | 15.8064 |
| 23906 | prefill chunk8192 and derived graph8192 | 2547.8540 | 98.8672% | 735.5602 | 16.3160 |

Matched mean goodput is2592.542986; report candidate gain against EACH run and
this mean:100*(candidate/reference-1). Report TTFT/ITL absolute changes as well.
A positive mean delta can still be below the better baseline; retain both
comparisons. Two close baseline runs do not supply a confidence interval or
prove future noise bounds. A faster single candidate needs independent repeat
before selection. Do not add standalone FlashInfer and MNNVL gains to predict
23904: interaction can change the bottleneck.

Before interpreting completed candidates, verify scheduler state/exit, sealed
artifact hashes, submitted worker/config, full60/120/30 phases and actual phase
timing, benchmark request/error/cancel totals, observed token lengths and raw
short-output cases. Confirm all8decode ranks initialize MNNVL and inspect the
requested attention backend when applicable. Preserve any startup failure as
INCOMPLETE and any complete SLA failure as measured failure. A populated
registry or COMPLETED alone does not replace raw evidence. Keep7/8 diagnostic
and organiser accuracy unverified; new output failures block promotion.

Some config provenance is inherited: source_experiment=s5-rr-repeat-n52,
control_job=22415 and reference_jobs=23325/23576. Those fields do not identify
the matched wave9 MNNVL comparator. source_job=23778 and the validated pair
23778/23839 identify this comparison. FlashInfer candidate config's
`decode_extra_flags` does not list the inherited dense CUDA graph flags, but
the actual worker retains the identical64-size graph list; chunk configs also
retain the old prefill_extra_flags4096 metadata while the actual worker uses
the intended2048/8192. Use the stored launcher plus hashed worker and runtime
log to determine execution. Frozen artifacts stay intact; this guide records
the metadata limitations explicitly.

No new repeat, higher-load extension or submission gate is installed here.
At the historical preflight, shared H200 cap5 was full;23924N54 is the existing wave7 continuation and
has no authorized automaticN56 extension. NSCC04→05 retains its independent
access, baseline, queue, credit and budget gates.

Evidence:[audit JSON](../nscc-pbs/inspection/wake-20261015-2150UTC/wave9-preflight-review.json),
[own scheduler/access snapshot](../nscc-pbs/inspection/wake-20261015-2150UTC/live-check.json).
Stored scripts, raw sha256 output and worker diffs are alongside the audit.


## Historical runtime audit — 2026-10-15 22:57:45 UTC

23904 RUNNING since22:51:04UTC on g1/g4;23905/23906/23924/23934 remain
PENDING(Resources) at22:57:45UTC. The five-job shared cap remains full and the
existing watcher is alive. This supersedes the all-pending historical snapshot.

23904 frozen and copied payload hashes, SHA256SUMS and Slurm-stored batch script
all match. Captured logs confirm all8ranks initialize MNNVL, hybrid FlashInfer
decode/FA3 prefill attention and NIXL/UCX. Both prefill instances use chunk4096;
decode graph sizes1–64 match; both P/D paths warmed successfully. Comparing
resolved ServerArgs against EACH of23778/23839 yields only the requested decode
attention change plus engine-generated random_seed differences. AIPerf's fixed
random-seed2026 is distinct from that unpinned server seed. Frozen payloads are
unchanged; this audit does not retroactively control seeds or quantify their
effect, nor does it establish deterministic output or noise bounds.

No full export or output-smoke result was available in this runtime audit;
initialization is not a measured speedup or accuracy result. Captured log
prefixes have hashes and timestamps, not final artifact seals. After terminal,
follow the checklist above and compare goodput/TTFT/ITL with both baselines.
No repeat/N56 is submitted by this audit.

Evidence: [runtime audit](../nscc-pbs/inspection/wake-20261015-2255UTC/runtime-review.json),
[final queue](../nscc-pbs/inspection/wake-20261015-2255UTC/final-queue.json).


## Terminal review — 2026-10-16 00:19:38 UTC

23904 completed exit0 at23:01:10UTC15Oct;23905 completed exit0 at00:05:14UTC16Oct.
At00:19:38UTC,23906/23924/23934 are PENDING(Resources), three of five allowed slots;
watcher3514431 remains alive. These final results supersede the earlier pending
and initialization-only descriptions for23904/23905.

Both candidate seals and BOTH baseline seals rehash successfully (47files each).
Frozen/copied payloads and earlier Slurm-stored scripts match;11common operational
files match each baseline, worker changes exactly the named CLI factor. Full
60/120/30 protocol and normalized client configuration match; actual phases:
23904 warmup63.205s/821requests, measured123.143s/1636requests;
23905 warmup63.832s/734requests, measured123.962s/1463requests. Zero request errors
and cancellations, both P/D paths warm, all8ranks initializeMNNVL andNIXL/UCX.
23904 also confirms all8FlashInfer decode ranks. Both short suites remain7/8,
only the independently documented reverse failure, with no newly failed case.
This remains research evidence; organiser accuracy has not been verified.

| Candidate | Gain vs23778 | Gain vs23839 | Gain vs mean | TTFT delta vs mean | ITL delta vs mean |
|---|---:|---:|---:|---:|---:|
| 23904 FlashInfer+MNNVL | +1.5016% | +1.4718% | +1.4867% | +122.9668ms | −0.9075ms |
| 23905 chunk2048+MNNVL | −10.0615% | −10.0879% | −10.0747% | +676.5036ms | −1.3345ms |

FlashInfer+MNNVL is a provisional single-run improvement, with a TTFT cost;
no repeat or promotion is performed here. Chunk2048 is a complete passing-SLA
measurement with lower goodput, not an incomplete or failed deployment. Lower
meanITL alone does not imply faster closed-loop serving when TTFT rises.

Runtime correction: the single chunk CLI factor also changes the resolved
prefill breakable CUDA graph max_bs4096→2048 and truncates capture sizes in
BOTH prefill instances. Other nested graph fields and decode graphs match.
Do not attribute the result solely to chunk scheduling or claim graph settings
were identical. The previously extracted image source server_args.py4723–4752
sets the default prefill graph maximum from chunked_prefill_size; current H200
ServerArgs independently establish the actual change. For pending23906, inspect
whether chunk8192 also resolves to graph8192; this is an expectation, not runtime
validation. The engine random_seed remains unpinned across allocations.

Raw output lengths:23904 spans199–201tokens (mean199.99878),23905 spans199–200
(mean199.99932); both baseline extrema are199–201. Raw profiling counts and token
sums/min/max match exports. Fixed200-token goodput uses the existing benchmark
convention, not a claim that every observed response has exactly200tokens.
Attempt01's overly strict max200 assertion was corrected; attempt02 exposed the
derived graph change. Both scripts and corrections remain preserved.

Next: collect23906 and the twoN54 jobs through the existing watcher; use the
same final-evidence checks and both matched baselines. No newrepeat/N56/job,
controller or schedule is introduced. NSCC04→05 still requires restored existing
access, terminal220575, passingN32 and fresh ownqueue/credit/budget checks.

Evidence: [final independent audit](../nscc-pbs/inspection/wake-20261016-0015UTC/wave9-final-review.json),
[source excerpt and provenance](../nscc-pbs/inspection/wake-20261016-0015UTC/prefill-graph-source.json),
[latest own queue](../nscc-pbs/inspection/wake-20261016-0015UTC/final-queue.json).


## Runtime chunk8192 — 16/10/2026 01:43 UTC

23906 RUNNING từ01:38:03UTC trên g1/g4; lần kiểm scheduler 01:43:17UTC:
23924/23934 PENDING(Resources),3/5slot; watcher3514431 sống. Các snapshot
23906PENDING trước01:38 là lịch sử. Chưa có phép đo hoàn chỉnh mới.

Audit01:41:56UTC: frozen/copied payload, registryhash và Slurm-storedscript đạt;
11file chung giống CẢ23778/23839, worker chỉ đổi chunk4096→8192. Runtime cả hai
prefill xác nhận chunk8192 và breakable CUDAgraphmax_bs8192; so baseline4096,
capture bổ sung4608/5120/5632/6144/6656/7168/7680/8192. Các trường graph khác
và decodegraph1–64 giữ nguyên. ResolvedServerArgs chỉ khácchunk/graph và seed
engine tự sinh. Cả8rankMNNVL/NIXL đạt; P/Dwarmup chưa hoàn tất tại snapshot audit,
không coi đây là startupfailure. Logprefix đã hash, không phải finalseal.

Tiếp: watcher thu23906 rồi kiểm terminalexit/seal/full60/120/30/rawmetrics,
shortnonregression và2P/Dwarmup; so CẢ23778/23839 vàmean2592,542986, kèmTTFT/ITL.
Không quy kết riêng chunk scheduling; không thêmrepeat/N56/job/controller.
NSCC01:40:59UTC helper thiếuVPN trướcSSH;220575/result/credit vẫn chưa xác minh.
Giữ1536SUreserve,campaign16384SU và04→05→06 gates; không xác thực mới/qsub.
Bằng chứng:`nscc-pbs/inspection/wake-20261016-0140UTC/`.


## Bàn giao 16/10/2026 01:47:27 UTC

Scheduler vừa kiểm tra: 23906 RUNNING từ 01:38:03 UTC trên g1/g4;
23924/23934 PENDING(Resources), 3/5 slot; watcher 3514431 sống.
Snapshot 01:43 trước đó là lịch sử. Chưa có final seal hoặc kết quả mới.

Audit 01:46:33 UTC xác nhận cả hai P/D paths đã warmup, 8 rank MNNVL/NIXL,
payload frozen/copied và script Slurm đã lưu đều khớp. Chunk8192 đồng thời
tăng graph prefill lên8192; decode graph giữ nguyên. Logprefix có hash,
chưa phải final seal. Trạng thái chưa warmup lúc01:41 đã được thay thế.

Đã chuẩn bị `nscc-pbs/inspection/wake-20261016-0145UTC/review-chunk8192.py`: chỉ đọc job23906 sau terminal/seal,
kiểm protocol60/120/30, raw request/good/latency/length, short non-regression,
runtime và so CẢ23778/23839 cùng mean. Replay hai baseline từ sealed artifact
đạt2592,1624/2592,9236 goodtokens/s; đây là dữ liệu cũ, không phải repeat mới.
Terminal path của công cụ chưa được kiểm bằng23906 hoàn chỉnh.

NSCC01:45:30UTC: helper thiếuVPN trướcSSH;220575/result/credit chưa xác minh.
Giữ1536SU reserve, campaign16384SU, pilot04→05→06 và gate hiện có.
Không xác thực mới/qsub, thêm job/repeat/N56/controller/schedule.
Tiếp: watcher thu23906 và haiN54; chạy review khi có finalseal.
Bằng chứng: `nscc-pbs/inspection/wake-20261016-0145UTC/`.

Read-only replay once watcher has sealed terminal23906:

```bash
python3 /home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nscc-pbs/inspection/wake-20261016-0145UTC/review-chunk8192.py
```

The command reports INCOMPLETE while running or unsealed. It does not poll,
submit jobs, change the watcher, or approve configuration promotion.


## Bàn giao 16/10/2026 01:52:34 UTC

23906 **COMPLETED exit0** lúc01:48:16UTC, đã được watcher thu và finalaudit độc lập.
Tại01:52:34 UTC:23924/23934 **PENDING(Resources)**,2/5slot;watcher3514431 sống.
Các snapshot23906RUNNING/chưa seal trước01:48 và pending trước01:38 là lịch sử.

Chunk8192 đạt **2547,8540 goodtokens/s**,SLA98,8672%,TTFT735,5602ms,
ITL16,3160ms;thấp hơn mean23778/23839 **1,7238%** (từng baseline−1,7093%/−1,7382%).
So mean,TTFT+223,2940ms dù ITL−0,8249ms. Full60/120/30,47file seal/mỗi run,
frozen/copied payload và script Slurm lưu trước đó khớp;789warmup/1589profiling,
0lỗi/hủy request;8rankMNNVL/NIXL,2P/Dwarmup;short7/8,chỉreverse đã biết.
Observed output200–201tokens,rawsum317801 khớp;goodput vẫn dùng convention200.
ChunkCLI đồng thời đổi prefillgraph4096→8192;decodegraph không đổi,engine seed
chưa khóa. Đây là một điểm đo đủSLA nhưng goodput thấp hơn,các kết quả không cô
lập hiệu ứng scheduling. Chưa chọn cấu hình hay xác nhận accuracyBTC.

Công cụ final đã chạy đạt trên23906;không còn chỉ là prototype chờ terminal.
Cả ba wave9 đã finalaudit;chỉFlashInfer+MNNVL23904 có lợi thế một lượt+1,4867%,
chưa repeat/chọn cấu hình. Tiếp:watcher thu haiN54,chạy`serving-tuning/review-n54.py`
và so cả hai baseline/mean. Không thêmjob/repeat/N56/controller/schedule.

NSCC01:50:59UTC helper vẫn thiếuVPN trướcSSH;220575/result/credit chưa xác minh.
Giữ1536SUreserve,campaign16384SU,04→05→06 và các gate hiện có;khôngauth/qsub.
Bằng chứng:`nscc-pbs/inspection/wake-20261016-0150UTC/chunk8192-final-review.json`;raw artifact giữ tại`runs/23906/`.

Final candidate phases: warmup62.995751311s/789requests;profiling123.319468811s/
1589requests,1571good. Output extrema200–201,mean200.0006293,sum317801.
All47files in each candidate/baseline seal rehashed. Runtimecopied logs now
terminal, replacing growing-prefix status in historical audits. The original
01:45 review remains an archived prototype; this run copied it into a new
inspection directory before execution, preserving previous evidence unchanged.

| Candidate | Gain vs23778 | Gain vs23839 | Gain vs mean | TTFT delta vs mean | ITL delta vs mean |
|---|---:|---:|---:|---:|---:|
| 23906 chunk8192+MNNVL | −1.7093% | −1.7382% | −1.7238% | +223.2940ms | −0.8249ms |

[Final review](../nscc-pbs/inspection/wake-20261016-0150UTC/chunk8192-final-review.json) and
[terminal runtime audit](../nscc-pbs/inspection/wake-20261016-0150UTC/runtime-review.json).
