# Research review: H100 native expert-replica diagnostic 224278

## Question and prior evidence

The parent experiment asked whether the pinned HPC-Ops `fuse_moe_blockwise` API could execute five sequential virtual expert-parallel (EP) partitions for 128 logical experts stored in 130 physical slots, with slots 128 and 129 exact copies of experts 0 and 1. The native outputs were to be checked against an EP=1 native control and an independent FP32 MoE calculation. Its CPU shape fixture had passed, but no GPU behavior had been established before submission.

The activation precheck compared the pinned SGLang quantizer against an independent PyTorch implementation that divided FP32 inputs by the computed scale, clamped to `[-448, 448]`, and cast to E4M3. The scale comparison passed. Exact FP8 bytes did not. Since this exception is raised before the first `hpc.fuse_moe_blockwise` call, the run provides no evidence for or against native expert replication.

## Hypothesis and exact run

Job `224278.pbs111` ran on one assigned NVIDIA H100 80 GB (SM90), with a deterministic seed of 2026. The fixed 16-row, hidden-size-256 BF16 activation and synthetic 128/130-expert weights were unchanged from the frozen parent. The exact source submitted to the cluster is preserved under `collected/hpc-ops-replica-primitive-20261024/runs/224278.pbs111/submitted/` and is byte-identical to the local frozen parent copy. In particular, `run_gpu.py`, the pinned SGLang FP8 source, and `SOURCE_PROVENANCE.json` all match by SHA-256.

The proposed explanation is a quantization-intermediate difference: the retained Triton kernel converts loaded input to FP32, computes `scale = max(abs(x), eps) / 448`, computes the reciprocal, multiplies by it, clamps, then casts to FP8. The independent reference divides by scale before the same clamp and cast. Near an FP8 rounding boundary, algebraically equivalent arithmetic can yield different bytes. The scale passing its tolerance makes a scale-shape or gross scale-computation mismatch less likely, but the current run retained no mismatch counts or values. The explanation is therefore plausible, not yet demonstrated.

## Observed result

PBS reports the job finished with `Exit_status = 2` and walltime `00:01:23`. The program's persisted partial JSON reports 23.645 seconds elapsed and the exact error `pinned SGLang activation FP8 bytes differ from independent group quantizer`, raised at line 196 of the submitted `run_gpu.py`. This is an early validation failure, not a kernel failure and not a pass.

The SGLang runtime image and source checks completed before the failure. The captured GPU samples show the assigned H100 UUID and 0 MiB used at both the initial and final sample. Those sparse samples do not establish utilization during execution, peak memory, kernel time, or a healthy hardware state. PBS accounting captured 1:36 CPU time, 1,136,716 KB memory, and 23,056,012 KB virtual memory. No phase-aligned hardware telemetry was collected.

## Evidence collection and inspection

The successful adapted collector preserved 30 terminal files totaling 303,573 bytes in `raw-evidence-attempt3.tar.gz`; its per-file size and SHA-256 manifest is `collected/evidence-sha256.json`, and every extracted file was rechecked against that manifest. The archive includes the exact submitted source, job log, stdout/stderr, partial result JSON, GPU samples, and PBS accounting. The earlier failed collector attempts remain present as raw artifacts so their path correction history is visible; they are not job-result evidence.

Inspected: PBS terminal state and exit status; complete retained error and stack trace; partial result JSON; job launcher checksums; exact submitted source identity; source provenance; before/after GPU samples; and available CPU/memory accounting. Not collected or not inspected: GPU utilization over time, peak VRAM, kernel durations, native MoE outputs, routed rank contributions, the FP32 oracle, and performance. These are unavailable because execution stopped before the native calls.

## Assessment and next decision

Preserve the parent's strict exact-byte failure as the historical result. Do not relabel the parent as passed, weaken its frozen gate in place, or infer that the native MoE path works. The next question is whether measured byte differences are consistent with the pinned reciprocal-multiply path and the finite E4M3 rounding bound, while the native MoE outputs remain within the predeclared numerical limits.

The prospective, unsubmitted protocol is in [`hpc-ops-replica-r2-20261024/README.md`](../hpc-ops-replica-r2-20261024/README.md), with a separate R2 runner and CPU-only bookkeeping fixture in that directory. It keeps the actual pinned quantized activation as the native input, records mismatch counts/fractions and byte pairs versus both direct division and reciprocal multiplication, checks dequantized error against a bound based on adjacent finite E4M3 values and the actual group scale, and writes partial metrics before numerical gates. The independent FP32 MoE oracle uses those same actual quantized inputs. Existing MoE relative-L2 `<= 2%` and duplicate-copy `<= 1e-7` limits remain unchanged. The CPU fixture validates only source provenance and diagnostic bookkeeping; it is not GPU or FP8 evidence. No R2 GPU result exists.

The parent benchmark's documented boundary remains: one GPU, synthetic dimensions, five serial local calls, and a local tensor sum. Even a future R2 pass would not prove multi-GPU communication, production SGLang routing/EPLB, Qwen accuracy, model-scale memory fit, or serving performance.
