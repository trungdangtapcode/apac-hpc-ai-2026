# Final H200 verification evidence — 31 October 2026

These nine full benchmark allocations used 16 NVIDIA H200 GPUs across Firmus nodes g1 and g4. The request workload used cold prefixes, seed 2026, 4,000 requested input tokens and 200 requested output tokens, with 60 seconds warmup, 120 seconds scored profiling and 30 seconds drain grace. Each request qualifies only when TTFT ≤ 3,000 ms and request-mean ITL ≤ 20 ms; at least 90% of requests must qualify jointly. Good output tokens/s is exported AIPerf Goodput (requests/s) × 200. The CSV reports SI-equivalent tokens/s and milliseconds.

`final-nine-run-ledger.csv` is the compact comparison. Each `jobs/<ID>/` directory includes the score export JSON and CSV, compact resolved-setting summary, and retained diagnostics. A request-level `profile_export.jsonl.gz` is included for all jobs with an available raw file; decompress with `gzip -dk`. Its source hash is recorded below. The roughly 228 MB `inputs.json` per job is excluded because it duplicates full input/request payloads; it is not required to read the score export. Each job's original config is reduced to public experimental fields, with node/container scratch paths and the full submitted payload omitted. Exact submitted bundles and full run artifacts remain in the research archive.

## Controls and interpretation

- 27777 is the fresh H200 incumbent control for the FA3, transferred full-recipe and chunk comparisons.
- 27826 is a separate explicit `no_grad` control for inference-mode ports; it is not the denominator for 27777-series comparisons.
- 27781 is N54; 27783 is N64. Do not compare 27781 directly to an N64 control as a matched load effect.
- The four distinct additional ports are 27804 (HPC-Ops chunk 6144), 27806 (HPC-Ops chunk 8192), 27828 (decode inference mode) and 27830 (prefill inference mode). This does not mean there were four H100 winners or four improvements.
- None of the final candidates established a useful gain above the team's prospective 1% decision gate against the applicable control. Keep the current H200 recipe: DeepGEMM prefill at chunk 8192; HPC-Ops decode, FlashInfer attention and MNNVL collectives; N64. NIXL is the KV transfer between prefill/decode roles.
- All nine passed the team's full local run gates. This is not the organiser's full-set model-quality test; official ≥99%-reference quality remains UNKNOWN.
- Hardware monitoring values, request tails, sampled VRAM, GPU activity and KV occupancy are different measures. Review the linked reports for collection scope and causal limits.

## Reviewed evidence

- `reviews/h100-derived-on-h200.md`: fresh control, FA3 and transferred recipe results; includes H100 vs H200 attribution and the N54/N64 tail analysis.
- `reviews/chunk-ports.md`: HPC-Ops chunk 6144/8192 interaction, both compared to the incumbent.
- `reviews/phase-mode-ports.md`: explicit mode control, actual provider activation checks and phase measurements.
- `integrity/README.md`: source/archive object integrity review. This packaged selection additionally records per-file hashes in `source-manifest.json`.

Actual cost across all nine final H200 allocations: 28.337778 GPU-hours; zero PBS SU. Historical H100 measurements and the earlier repeated H200 operating mean are separate series; they are not pooled into these fresh-control comparisons.
