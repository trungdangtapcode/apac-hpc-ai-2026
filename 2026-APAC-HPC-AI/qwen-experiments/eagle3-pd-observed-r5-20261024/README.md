# Conditional H100 observed EAGLE3 correctness attempt

R5 is derived from the reviewed but unsubmitted R4 candidate. R4 was correctly blocked when its parent224275 failed before model loading. This new frozen candidate requires **afterok:224276.pbs111**, and independently reads and retains that corrected parent's actual passing four-rank observer receipt before starting any model worker. Parent failure prevents execution.

The native NIXL912b7 source, FP8 target/BF16 draft, TP4/TP4/TP8 topology, disabled prefill graphs, actual16rank metadata gate, two semantic P/D path checks and exact1600output-ID/reference comparison are unchanged. The parent's numerical correctness and official accuracy limits remain in `PARENT_ROOT_REVIEW.md`. New runtime differences are canonical bundle paths and the corrected prerequisite. CPU launcher, absolute-deadline, semantic and observer-import fixtures pass.

This requests two exclusive H100 nodes /16GPUs /at most30minutes, conservative maximum1024SU. It is a transport/output-correctness diagnostic without AIPerf or score. No EAGLE speedup is claimed. Every stage is bounded from batchT0 within1530seconds before the1800second PBS limit.

Do not treat this prepared README as a job receipt. Root must capture the final frozen payload and recheck actual combined PBS capacity, selected AI credit and parent status under CPU-before-AI locks before qsub. No CPU/HPC payload is changed.
