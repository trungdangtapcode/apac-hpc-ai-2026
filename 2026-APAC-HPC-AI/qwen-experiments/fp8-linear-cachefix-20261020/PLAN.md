# Repair cache provisioning without changing the kernel experiment

222210 failed on all eight ranks before measurement: importing FlashInfer tried to create its default workspace below read-only /home/users. No kernel timing, numerical case or model result exists. [Sealed failed-run review](../fp8-linear-micro-review-20261020/RESULTS.md). Estimated cost is 20.480 SU for 72 seconds; retain its previous maximum reservation until the published ledger posts the final charge.

Derived v2 adds explicit, unique job/rank temporary cache paths before Torch/SGLang/FlashInfer imports, including FLASHINFER_WORKSPACE_BASE and Torch extensions, plus a writable-directory probe. HOME remains unchanged. The actual imported FlashInfer workspace must lie under the configured base. Write a per-rank cache preflight artifact before imports, so later failures remain attributable. Cache paths are disposable and contain no authentication state.

The experiment config, driver/run script and bench tail from torch.manual_seed onward are byte-identical to v1. Same synthetic FP8 weights, shapes, backend selection, graph operations, replay counts, numerical/input-integrity gates and post-timing traces. No kernel, dtype, timing threshold or workload relaxation. Native source-hash guards remain strict.

Validation executes the exact deployed FlashInfer workspace AST under an unwritable-home fixture, first reproducing the old default path, then verifying workspace/JIT/generated directories for eight distinct routed ranks are writable and HOME unchanged. Reproduce with python3 validate-cache.py. This CPU fixture checks the concrete failing dependency path; it does not prove GPU imports, kernels or timings will pass. Python and shell syntax and unchanged experiment-tail checks pass.

Submit one bounded H100 retry (8 GPUs, 10 minutes, max170.667 SU) after a fresh queue/credit check. Reconcile the failed charge only if its 20.480 SU delta matches published Used; otherwise keep the old max170.667 conservative reservation in addition to the new maximum. Respect unchanged 51000 cap/13000 buffer, one running PBS allocation and three active cap. No uncertain qsub retries.

For H200, replace only the pending standalone micro24983 with the derived portable cache harness. Use a pending-state-only cancellation under the shared watcher lock, preserve its old script/receipt as a cancelled unmeasured attempt, check real active count before resubmitting, and retain all four original model job positions/bytes. If the old micro has started, do not kill it or exceed five active jobs; retain the prepared fix for a later feasible step. Never edit a submitted bundle in place.

The original kernel screen hypothesis and advancement gates remain in ../fp8-linear-micro-20261020/PLAN.md. No model loading, new serving record, official accuracy, clock/power change, package edit, VPN restart or background Codex.
