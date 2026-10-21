# Shell-dispatch correctness repair submitted

Definite receipt **223055.pbs111**, submitted **2026-10-21T14:35:54.369564+00:00**. [Dated live snapshot](live-initial.json) shows R. Allocation: **16 H100, at most 30 minutes, maximum 1024 SU**. This is a real-token correctness diagnostic, not ranked performance.

The parent 223053 reaches all-role/router readiness, then external timeout cannot execute the exported srun shell function. R3 invokes that exact function through child Bash within the same timeout, preserving every argument, absolute deadline, native inference, container adapter and 1600-ID gate. Six CPU launcher fixtures and nine semantic fixtures pass. [Plan](PLAN.md), [CPU results](launcher-validation.json). Local mocked process cleanup is not proof of remote PBS task termination.

Fresh locked pre-submit AI ledger: **Used 45633.701 SU**, **Balance 17342.299 SU**, **In Doubt 1024 SU**. Balance already excludes In Doubt. No new posted charge delta appears, so parent 223053 retains its full **1024-SU** maximum despite its estimated actual **288.426667 SU** cost. Reserve the new **1024-SU** maximum separately. Conservative internal headroom is **3318.299 SU** under unchanged **51000 cap / 13000 reserve**. No maximum is released without unique reconciliation. [Reconciliation](reconciliation.json), [receipt](pbs-receipt.json).

Own GPU queue was empty before qsub. One conservative external CPU slot allowance is retained; no HPC server access, jobs or ledger changes. H200 queue positions are preserved. No automatic Codex schedule.

Peer review confirms the runtime repair and identifies local validation sidecars omitted from the immutable runtime manifest. They are retained separately with [hashes and recovery scope](validation-evidence.json) and validation-evidence.tar.gz, captured together with the complete source directory. The remote runtime payload does not contain those local sidecars; Git recovery does. No frozen payload is rewritten.

Next: collect and seal terminal state; inspect native worker graphs/dtype/NIXL, actual heterogeneous transfer, real output IDs, speculative metadata, errors, hardware coverage, locality and cost. No new score or complete output-equivalence result yet. Keep H100/H200 series and official accuracy separate. A valid useful pass is required before a fresh matched-capacity short screen.
