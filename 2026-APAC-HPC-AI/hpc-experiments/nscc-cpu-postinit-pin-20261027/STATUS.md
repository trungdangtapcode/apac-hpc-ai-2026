# Native post-initialization pin qualification admitted

Job **26016270.pbs101** was submitted once at **2026-10-27T03:26:53.864618+00:00**. The fresh scheduler check at 03:27:37 UTC on 27 October reports Q/q5 waiting for `node_pool`. Both own CPU and AI queues were empty before admission.

The job requests four exclusive CPU nodes, 512 ranks / CPUs, zero GPUs and a five-minute maximum. Maximum reservation is 42.666667 SU at the verified one SU per CPU-hour rate. The baseline native probe is byte-identical to its predecessor. The candidate selects one online allowed logical CPU per validated physical core using actual MPI local ranks, pins its calling thread after MPI initialization, then audits immediate and later collective/delayed masks. No solver or preload runs. Existing MPI helper threads and NIC placement remain unqualified.

Offline fixtures and strict C syntax checks with a declaration-only MPI shim pass; real site compilation and mask stability are still unverified. Runtime failures propagate to worker status. Never call this a performance result before actual logs pass. Source is frozen; inspect the explicit receipt and retained intent before any retry.
