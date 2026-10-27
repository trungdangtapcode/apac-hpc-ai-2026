# Actual Pstream integration gate admitted

**26019383.pbs101** was submitted once at **2026-10-27T05:24:00.607094+00:00**. At 05:25:41 UTC on 27 October, PBS reports Q/q5 waiting for `node_pool`. Both own CPU and AI PBS queues were empty immediately before admission.

The frozen job has three arms: unchanged native MPI control; the same control through the PMPI adapter; actual parallel OpenFOAM checkMesh through the adapter on an owned 8,192-cell mesh. It requires complete initialization, physical placement, pre-finalization and actual post-PMPI_Finalize return audits for every adapted rank. This is an integration qualification, not a DrivAer solver run or score.

Request: four exclusive nodes, 512 CPUs/ranks, zero GPUs, 600 seconds maximum. At the verified rate one, maximum reservation is **85.333333 SU**. Internal commitment is now **4,857.2 SU**, leaving **24,920.646667 SU** under the unchanged ceiling. Older unknown maxima remain retained; the site balance still carries its dated backend label and is not individual posted billing.

No real adapter ABI/runtime claim exists until actual compilation and all three arms pass. Any missing audit, work failure, hash change, wrong application version/rank/cell count or nonzero PMPI finalization return fails the gate. Preserve the submitted payload; do not retry an existing intent blindly.
