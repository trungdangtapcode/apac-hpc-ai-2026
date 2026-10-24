# Submitted topology diagnostic — 25956623.pbs101

Submitted once on 24 October 2026 after reviewing the three completed jobs. The fresh 03:12:23 UTC PBS check shows **Q/q5**, insufficient `node_pool`. Preserve the intent and frozen payload; no repeat submission. CPU and AI PBS queues were both empty in the locked pre-admission checks. No dependency is needed because all three preceding jobs are terminal. Only this new CPU diagnostic was admitted.

The request is 4 exclusive CPU nodes ×128 ranks/CPUs, 32 GB/node, 0 GPUs and 3 minutes, with a 135-second internal deadline. Maximum reservation **25.6 SU**. C compiles on the allocation. Per-rank pre/post MPI affinity and separate core/NUMA result diagnostics distinguish the previous combined failure. Scientific assignment, strict identity/candidate validators and transport/binding settings are retained. Candidate can launch only if all identity topology gates pass. No solver or measured speedup.

Local singleton-positive and multi-CPU-negative C tests use synthetic MPI declarations only. The randomized placement suite retains one positive and seven negative tests. Actual Cray MPI behavior and physical mapping remain unverified until the job finishes.

CPU campaign commitment after admission is **4,713.8 / 5,000 SU**, leaving **286.2 SU**. Unknown shared maxima remain unchanged. These are conservative planning allowances, not exact posted charges. Admission pins the sealed payload and reviewed earlier outcomes, checks fresh queue rate/balance and preserves one active CPU allocation / combined PBS cap three.

After completion, collect all TOPOLOGY_JSON records, stage codes, stdout/stderr, source seals and authoritative terminal resources. Identify the failed subcheck before any new fix. A pass can establish only this allocation/mapping; instrumentation itself is not proven to fix the original cause. Do not launch a full solver A/B until mapping and budget gates pass.
