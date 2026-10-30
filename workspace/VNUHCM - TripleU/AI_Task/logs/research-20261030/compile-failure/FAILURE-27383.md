# Actual Qwen compile failed before measurement

Reviewed 29 October 2026, Vietnam time (UTC+7). Actual job 27383 ended **FAILED 1:0 after 3:35** on g1/g4, 16 H200. **No AIPerf measurement or score exists.** Preserve the failure; do not count it as a completed performance trial.

The candidate enabled native decode torch.compile up to batch 54, retaining the original 1..64 graph list. The first compiled shape, 54, reached Qwen3 attention. The actual traceback enters qwen3_moe.forward_prepare_native, apply_qk_norm_rope and rotary_embedding/base.py forward_native, then raises:

    AssertionError: fused_set_kv_buffer_arg is not supported for native implementation

This is a native interface incompatibility, not an exhausted 600-second startup deadline. Eight current distributed decode receipts bind the actual job, experiment and native source. They retain successful ordinary capture evidence for larger noncompiled shapes and incomplete evidence at the first enabled compile shape; the full all-shape compile gate never passed. The independent one-GPU tiny fixture 27340 proved its own small-module interface only and did not establish Qwen compatibility. That prior limit is now concretely demonstrated.

The controller never reached ALL_WORKERS_READY, and no profile_export_aiperf.json exists. Local smoke/retrieval and official accuracy are unmeasured here. Startup hardware samples are retained but are not ranked-phase performance or hardware-health proof. Raw trace, every receipt, worker cleanup and terminal accounting are sealed in runs/27383/artifact-manifest.json. Observed occupancy is 0.955556 GPU-hours versus maximum 4.533334; zero PBS SU.

Decision: close unchanged S105 and block unchanged sparse-graph compile S108. Reducing graph bucket count cannot repair this interface assertion. Continue the independent compile-off sparse graph trial after its own source/fixture review; its startup and padding question remains valid. Investigate a source-supported fusion/compile compatibility setting before considering any new compiled Qwen trial, with a matching control if that setting changes serving behavior. No frozen submitted source was changed, no old queue position cancelled, and no submission or HPC payload was updated.
