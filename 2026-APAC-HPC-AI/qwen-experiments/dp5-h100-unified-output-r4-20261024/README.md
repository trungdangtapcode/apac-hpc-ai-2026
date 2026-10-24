# D5 unified output qualification (H100, R4)

This sealed derivative tests whether the five-GPU Qwen topology can start in unified mode and produce bounded smoke and retrieval responses. It follows the R3 startup proof; it does not claim official accuracy, a ranked score, or throughput.

The pinned SGLang source sets `disaggregation_mode` to `null` when unspecified. The worker removes decode-only, NIXL, and bootstrap flags and records the resolved per-rank mode. It also disables the prefill CUDA graph and retains decode graph batch size 4. The runtime head check requires the unified mode on all five ranks before making local requests.

After startup gates pass, the worker records eight smoke responses and twelve synthetic retrieval responses on loopback port 30150. The 7/8 smoke reference is an observation floor; response counts do not gate readiness. Raw responses and HTTP errors are retained. `official_quality_status` remains `UNKNOWN`; no scored load or throughput claim is made.

The controller walltime is 17 minutes. The inner limits are 660 seconds for startup, 60 seconds for smoke, and 90 seconds for retrieval, leaving time for preflight and teardown. A five-second bounded sampler records available telemetry; missing values remain missing.

R4 requires a root review before `prepare_check.py` permits execution. No scheduler action is performed while this review is pending. See `R4_PLAN.json` and `R3_PARENT_PROOF.json`.

## Root review and acceptance

The completed R3 receipt, actual readiness result and independent terminal review are copied as portable, hash-bound parent proof. The prepare guard verifies those bytes and job identity before model work. The root output checker independently recomputes all raw responses and rejects any request error, new known smoke regression, fewer than 7/8 smoke passes or fewer than 12/12 retrieval passes. A failed output screen does not erase the separately recorded startup readiness pass. No official accuracy or throughput claim follows from this local screen.

The native server lifetime is bounded at 900 seconds so it covers the startup and both diagnostic windows. Metrics are enabled and sampled every five seconds; no heavy profile or ranked load is added.
