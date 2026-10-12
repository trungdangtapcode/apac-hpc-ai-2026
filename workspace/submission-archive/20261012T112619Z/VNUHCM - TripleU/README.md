# VNUHCM - TripleU — APAC HPC-AI 2026 submission snapshot

Prepared UTC: **2026-10-12T10:24:13.693598+00:00**. Team label follows the requested directory name. This is a **Qwen evidence package with an explicit incomplete HPC section**, prepared for review/upload. Nothing has been sent to the organisers.

## Current best measured result

**P8-TP4_D8-TP8-EP8, N48, job 22415, transport patch `hetero-tp-request-descriptors-v1`:** **1912.30 good tokens/s**, **97.44% SLA**, 0 errors/cancellations, long 60/120/30 measurement. The slides and raw evidence now include this result. It is a local measurement, not an organiser score. Full-set accuracy remains untested.

The portable `submit.sbatch` below retains the earlier unpatched Basic replay (job 22219). The new winning stack is supplied as raw evidence and a reviewable patch with its historical payload, and is not silently enabled in that portable wrapper.

## Declared AI configuration

**Basic: P8-TP4_D8-TP4-EP4, N40, 16 H200, official published FP8 checkpoint, unpatched provided serving image.** Two prefill workers (TP4/EP1) on one node; two decode workers (TP4/EP4) on the other. All official requests use PD through the OpenAI-compatible gateway. No draft model/speculative decoding, approximation, expert/layer skipping or additional quantization is used.

Job **22219**, long internal confirmation (60/120/30), achieved **1666.01 good output tokens/s**, **97.82%** SLA fraction, **1034/1057** good requests, 0 errors and 0 cancelled requests. This is **local evidence, not an official organiser score**. The mean TTFT was 1229.46 ms and mean ITL 17.11 ms. The full accuracy gate remains untested.

## Files to review

- [Presentation](Presentation/TripleU_APAC2026_Presentation.pptx): English slides with Vietnamese speaker notes; matching PDF and Markdown guide included.
- [Build and replay instructions](AI_Task/job_scripts/BUILD_AND_RUN.md), [single Slurm entry point](AI_Task/job_scripts/submit.sbatch), [environment](AI_Task/job_scripts/environment.json).
- [Results and raw evidence](AI_Task/logs/RESULTS.md), [coverage of the 17 topologies](AI_Task/logs/COVERAGE.md).
- [NIXL research and current best stack](AI_Task/job_scripts/supplementary/README.md): not enabled by the declared entry point; local speed evidence is included, accuracy remains unverified.
- [HPC status](HPC_Task/job_scripts/README.md): no OpenFOAM results or scripts available.

## What remains outstanding

1. Full-set accuracy check: at least 99% of the organisers' FP8 reference score. No such pass is claimed.
2. Organiser reconstruction and official re-run; the portable packaged wrapper has only CPU/static validation so far.
3. All 17 usable layouts have been measured: 14/17 original configurations and 3/3 EP2 replacements. Three incompatible EP1 originals remain explicitly blocked; failed runs are not counted as measurements. Promote and GPU-validate a portable replay of the new winning stack before using it as the primary entry point.
4. HPC deliverables if the organisers require both tasks for this entry. The general published rules require Basic for each task; the user's active work scope here was Qwen only.

The organiser-provided .sqsh images and checkpoint are deliberately external; use the exact recorded shared-storage files. No private credentials or writable container-home directory is packaged. The root checksum and file manifest support integrity checks after extraction.

## Archive/upload

The sibling ZIP contains this directory as its top-level folder. Upload through the organiser's designated channel. This workspace does not contain a confirmed upload address or submission receipt; archive creation is not submission acceptance.
