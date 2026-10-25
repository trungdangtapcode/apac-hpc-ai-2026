# Phase-isolated native QK normalization and RoPE fusion

S66 enables the existing fused kernel on both prefill workers only. S67 enables it on decode only. Compare both with fresh round-robin control 26083; all three use N64, 4000/200, seed 2026, 20/40/30 and 16 H200 GPUs. Each requests at most 17 minutes. Require >=3% gain and every local gate before full confirmation. Official accuracy remains UNKNOWN.

The exact deployed image source is retained with SHA256 values in verification.json. Qwen3MoeAttention selects this path only for compatible rotary embedding, supported head dimension and successful native BF16 JIT build. Both candidates mount a model source differing solely by two startup observer lines, preserving arithmetic. Per-rank native selection must be true on the intended roles and false elsewhere before scoring. A requested flag alone is insufficient. Actual kernel invocation/timing is not traced and must not be claimed.

The 130-config bounded serving-directory scan found no explicit fusion study; this does not certify all historical artifacts. CPU fixtures replay real 25947 startup logs with clearly synthetic selection markers to verify the gates, including fallback/wrong-flag rejection. No GPU compatibility, output correctness or performance result is inferred from CPU fixtures. Frozen parents are unchanged.

An earlier scheduling-option probe is retained in h200-decode-steps-20261025 but did not justify a submission: the examined native scheduler files did not show an active continuous-decode-steps use. This bounded negative search is not proof of a global no-op. Its first extraction attempt failed because this host's old unsquashfs lacks -cat; selected-file extraction then succeeded. No GPU was allocated for that CPU investigation. We selected native phase-isolated fusion instead.

Question and prior evidence: recent S63 load growth lost goodput and worsened TTFT while mean ITL stayed under 20 ms. This does not identify a causal bottleneck, but motivates separate prefill latency and decode launch/memory interventions. Fusion can reduce intermediate operations; the GPU benefit and numerical effect remain unknown. Do not pool hardware scores or reopen unchanged losing branches.

Exact change: S66 prefill-only flag; S67 decode-only flag, source hashes and native per-rank selected checks. Their parent is frozen S65 control. All fixed workload, model/image/precision/kernel defaults, P8-TP4/D8-TP8-EP8, round-robin, runtime/KV/semantic/output and raw denominator checks remain. Source observer adds only startup logging and no scored per-call work. Each uses 16 H200/two nodes/17-minute cap/no PBS SU. Controls must pass; no substitute historical control if 26083 fails.

Decision: prepare two bounded screens, advance only >=3% over actual 26083 with all local gates; otherwise close that phase arm. If useful, require independent full-protocol confirmation and official accuracy assessment before adoption. Preserve tail/error/concurrency, role queues/KV/GPU/CPU/transport evidence and mark missing data explicitly. At preparation no new job ID or measurement is claimed.

Source route: qwen-experiments/h200-fused-qk-rope-20261025; immutable candidates in serving-tuning-11; exact source model qwen3_moe.py lines 517–531 and 598–624, kernel can_use helper lines 101–130; verify.py/verification.json label CPU fixtures honestly.
