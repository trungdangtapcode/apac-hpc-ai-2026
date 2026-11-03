# Accepted, then rejected by policy parser

Job **2294674** was accepted at **3 November 2026 11:31:21 Vietnam** after fresh empty-queue checks and a locked reservation. It ended **FAILED 1:0 after one allocated second** before any copy or solver work.

The compute node successfully reported interleave policy for both memory nodes, using the actual numactl key `interleavemask: 0 1`. Our parser only recognized `interleave` and `interleave node mask`, so it incorrectly read an empty mask and rejected the preflight. This is a parser portability defect, not evidence that Iris rejects interleaving. The raw output and structured failure are retained in terminal-evidence and terminal-inspection.json. No performance result exists.

Actual allocation: 56/3600 = 0.015556 CPU-hours, conservatively charged 1. Original maximum 9.333333 retired once; ledger 985 consumed, zero reserved, unchanged stage1009. Frozen payload is preserved. A separately derived retry must include the observed-key regression fixture, fresh hashes, a new reservation and scheduler receipt.
