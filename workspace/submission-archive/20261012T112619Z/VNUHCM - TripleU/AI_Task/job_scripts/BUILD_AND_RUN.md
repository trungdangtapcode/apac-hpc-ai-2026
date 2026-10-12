# Reconstruct and run the declared Basic stack

This package uses the exact organiser-provided SGLang and AIPerf enroot images on Firmus shared storage. No custom serving source or image build is needed for the declared result. `environment.json` records image SHA256, image sizes, image package versions, model metadata hashes and the pinned tokenizer revision. Obtain those exact images and the published FP8 checkpoint from the organisers if the shared files are not already staged. A replacement image built from package version numbers alone is not claimed to be identical.

## Prerequisites

Slurm with enroot/Pyxis, the Firmus H200 nodes, active InfiniBand, shared `/scratch`, `curl`, Python 3 and standard shell tools. Container images and model remain external to this archive. No weights are copied, trained or requantised. The offline tokenizer cache is included, so the replay does not depend on the team's account or Hugging Face credentials.

## Prepare and submit

From an extracted package, go to `AI_Task/job_scripts`:

```bash
cd 'VNUHCM - TripleU/AI_Task/job_scripts'
bash setup.sh --check
# Optional full verification of the two external image files (~25 GiB + 779 MiB):
bash setup.sh --verify-images
sbatch submit.sbatch
```

If submitting from another directory, pass the absolute `AI_Task/job_scripts` directory using `sbatch --chdir=...`; this is required because Slurm executes a spooled script. `setup.sh` creates the Slurm output directory before submission.

The single submitted job allocates two nodes / 16 H200, starts 2 prefill workers (TP4/EP1) on node 0 and 2 decode workers (TP4/EP4) on node 1, starts the gateway on port 8000, initializes all four P/D paths through temporary gateways, shuts the temporary gateways down, then invokes the exact official AIPerf command once at N40. The official command still performs 60s warmup + 120s measurement + 30s grace. The temporary setup prompts are separate from the official dataset and seed, as allowed by Q1.

Results are written under `AI_Task/logs/reruns/<job>/official/n40/`; Slurm output is under `AI_Task/logs/slurm/`. AIPerf uses its default artifact directory because no extra flags are appended to the locked official command. Only the main `/v1/chat/completions` gateway is targeted by the official client. Per-worker logs record UCX device selection and GPU visibility.

All environment paths can be changed via `TRIPLEU_SGLANG_IMAGE`, `TRIPLEU_AIPERF_IMAGE`, and `TRIPLEU_MODEL_PATH`, exported before submission. They must still resolve to the exact staged files recorded in `environment.json`. The declared concurrency remains 40. These path overrides do not change model or benchmark settings.

## Provenance and validation status

The worker script, pair-initialization script, placement and metric parser come byte-for-byte from measured job 22219. The new wrapper makes paths relative to this package, removes exploratory sweeps and invokes the literal official command. A text diff against the measured wrapper is included. Static shell checks, protocol argument checks, topology checks and metric reproduction are recorded in `../logs/package-validation.json`. **The portable packaged wrapper has not yet been executed on GPU.** Existing job 22219 is performance evidence for the underlying configuration, not a claimed run of the new wrapper.

`archive/` holds original frozen payloads, including old absolute paths, for audit only. Run `submit.sbatch`, not archived scripts. The supplementary NIXL patch is not enabled by this Basic entry point.

## Accuracy

No full-set accuracy run or reference quality score is available in this workspace. We do not claim the 99% reference accuracy gate is passed. Organiser reconstruction, accuracy testing and official performance re-verification remain outstanding.
