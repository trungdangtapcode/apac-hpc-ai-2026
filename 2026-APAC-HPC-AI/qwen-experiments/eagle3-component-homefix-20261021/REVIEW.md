# Component review: 222729.pbs111

Reviewed 2026-10-21T04:45:42.238481+00:00. Terminal PBS state F / exit 1, allocated walltime **64 seconds**, estimated **2.275556 SU**, pending unique posted-cost reconciliation. Submitted payload checks and raw evidence seal pass.

The actual native /generate synthetic gateway gate passes again. Writable private HOME permits native SGLang imports, resolving the preceding environmental failure. The next assertion compares str(torch device.uuid) directly with the scheduler's GPU-prefixed CUDA_VISIBLE_DEVICES and fails. The assertion also checks the H100 name. Neither actual value was written before failure, so this evidence does **not** establish a formatting-only mismatch or the wrong GPU. Native registry/configuration and tensor validation were not reached.

The failure is in the diagnostic, before model instantiation or inference. No target/draft model was loaded, no PD state moved, no greedy comparison or scored throughput exists. Gateway markers are synthetic. This is not a serving regression or a speedup. The container reports extraction fallback; image startup remains a component-cost limitation. No scored utilization, queue/KV state or latency exists in this job, and no hardware time series was collected.

Next derive a payload that records raw scheduler and Torch UUID values before validation, parses strictly as complete UUIDs (allowing the standard NVIDIA GPU- prefix), and requires identical 128-bit identities, one visible GPU, H100 name and SM90. Include an independent nvidia-smi UUID/name lookup for the allocated device. Do not relax device isolation or change native model/config/tensor gates. Test malformed, truncated and mismatched UUID rejection on CPU before spending. Preserve the original payload unchanged.

Raw evidence: [collection](collection.json), [sealed run](collected/222729.pbs111/evidence-sha256.json). The actual GPU UUID representation remains unknown until the new allocated observation.
