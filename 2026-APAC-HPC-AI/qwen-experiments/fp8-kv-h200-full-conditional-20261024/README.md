# Conditional full H200 KV precision pair

This draft reserves a matched full-protocol followup only if the completed 25863 BF16 control and 25864 FP8 screen both pass their preserved source checkers and the FP8 screen exceeds BF16 good output throughput by more than 1%. The paired jobs use N64, deterministic synthetic 4000/200 input/output, seed 2026, and a 60-second warmup, 120-second measurement, and 30-second grace. The only changed serving factor is KV cache dtype.

The S50 control is conditional on S48 job 25864 completing and passing. S51 is afterok the actual S50 job and independently requires a passing full-control artifact and root-bound artifact path. Guard skips occur before model workers and are not counted as measured experiments. Missing or invalid evidence fails closed.

Both full runs retain the existing runtime KV proof, resource telemetry, capacity/backend/graph gates, output smoke floor/no-new-regressions check, and 12-case long-context diagnostic. These local checks are not formal accuracy evidence. Quality remains UNKNOWN; there is no official >=99% claim. The full run has a hard 17-minute limit. If startup and all required checks cannot fit, it must stop without mislabeling a shortened run as full.

See [PLAN.json](PLAN.json). Canonical drafts are [S50](../serving-tuning-10/s50-h200-bf16-kv-full) and [S51](../serving-tuning-10/s51-h200-fp8-kv-full). No job is submitted and no queue or budget state is changed.

## Root-bound scheduler chain

Full BF16 control25875 follows afterok25864. The full FP8 treatment follows afterok25875 and is bound to that actual full-control artifact directory. Both replay the real short-screen evidence; only an improvement strictly above1% permits model workers. A valid loss is an explicit unmeasured skip, while missing or invalid evidence exits2. The treatment also requires the full control's measured checker and submitted manifest. This is prospective conditional admission, not a claimed screen win or official accuracy result.
