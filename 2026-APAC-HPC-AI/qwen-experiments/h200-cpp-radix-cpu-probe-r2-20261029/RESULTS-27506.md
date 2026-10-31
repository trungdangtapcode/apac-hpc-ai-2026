# CPU radix-tree prerequisite: terminal result

Reviewed 2026-10-31T09:54:58.497091+07:00, Vietnam time (UTC+7), against retained output and fresh Slurm accounting. This is retrospective completion documentation; the owner stop remains in force.

Job **27506 completed 0:0 in 95 seconds**, four CPUs, 16 GiB and **zero GPUs** on g4. The frozen payload pin check passes, runtime source hashes match their pinned versions, both synthetic CPU data-structure fixtures pass (page sizes 1 and 16), the deadline supervisor child exits zero, and native cleanup is observed. Page 16 is a metadata fixture only; it does not qualify page-16 KV semantics.

Cold extension JIT/import took **26.605 seconds**. Container creation took 56 seconds; the internal batch timer reports 92 seconds, a different scope from the 95-second scheduler allocation. Allocation occupancy is about **0.105556 CPU-hours**, below the 0.4 CPU-hour request cap, with zero GPU-hours and zero PBS SU. No CPU utilization or bandwidth profile was collected.

The inspected files are the scheduler row, probe.json, deadline-supervisor.json, compiler-import.log, host-start.txt, and original Slurm stdout/stderr. The retained probe source hashes agree before and after loading; Torch reports no CUDA device. The original stdout is not regenerated. A retrospective artifact-manifest.json seals the saved bytes, and result-27506.json records exact checks and scopes.

This is **not** a full Qwen/RadixCacheCpp integration test, P/D correctness test, quality evaluation or inference-throughput result. It supplies no good output tokens/s. Original 27387 remains failed; a larger allowed process window let the replacement finish but does not establish faster serving. No GPU follow-up is submitted while research is stopped.

The final report already mentioned this CPU success, but RUNS.md and this experiment's STATUS.md had not been advanced from admission, and the original runs/27506 paths had not been captured. A hash audit confirms that all four raw files already had byte-identical captured copies in the final delivery and its review stage. This review closes the terminal-review/canonical-path-seal gap rather than discovering a new performance result.
