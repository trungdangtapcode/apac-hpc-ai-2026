# H100 kernel pilot failed before measurement: cache directory

## Observation and provenance

222210.pbs111 is terminal F, exit1, allocated walltime 00:01:12. The immutable own-job snapshot passes submitted payload hashes; all eight rank stderr files are sealed and report the same import failure. FlashInfer JIT core calls `os.makedirs(jit_env.FLASHINFER_WORKSPACE_DIR)` during import and reaches the read-only `/home/users` hierarchy. No rank report or timed/numerical kernel case exists. This is **HARNESS_IMPORT_FAILED_NO_KERNEL_MEASUREMENT**, not a measured kernel loss, SLA failure or model accuracy result.

The previous script routed Triton/Inductor/DeepGEMM cache variables but omitted `FLASHINFER_WORKSPACE_BASE`. The exact deployed FlashInfer jit/env.py defaults its base to Path.home(); the actual dependency source is retained beside this review. An older successful collective micro already explicitly routes this variable, demonstrating a known container requirement. The omission is a harness defect and should be fixed before retrying.

## Cost and limits

Eight GPUs for 72 seconds estimates **20.480 SU** at the existing rate. The current published ledger still shows Used37215.572, Balance26613.761, In Doubt170.667 (old maximum prepayment). It has not yet posted the final 20.480 charge; retain the entire prior 170.667 maximum reservation until the published delta matches. Never subtract both prepayment and maximum reservation twice. A bounded new retry may keep this terminal-pending-ledger reserve conservatively if the aggregate stays within the unchanged cap/buffer.

## Assessment and repair decision

Do not infer Triton/DeepGEMM performance from an import error. Preserve the failed payload, account, stderr and terminal manifest. Prepare derived v2 bundles with all dependency caches explicitly routed into unique writable job/rank temporary directories **before imports**, keeping HOME unchanged and all kernel/numerical/timing settings intact. Validate against the exact extracted FlashInfer workspace expressions, test per-rank uniqueness/writability and syntax before submission. Do not modify the original frozen bundles.

The four H200 model jobs remain Priority-pending and untouched. The standalone H200 micro24983 is also pending; its harness has the same omitted explicit FlashInfer cache route. A pending-only replacement with a validated derived bundle can prevent a repeat setup failure, but cancellation is restricted to that isolated micro, never the four model queue positions. Record any cancellation and replacement IDs separately, and guard real queue counts under the shared lock.

This is an environment repair, not a changed research hypothesis or relaxed numerical gate. GPU kernel execution still requires validation after the fix. No model, official accuracy, successful micro timing, VPN authentication, package change or background AI is claimed.
