# Static locality result: an allocation-specific mismatch, not a serving bottleneck

Job **222412.pbs111** finished with exit 0 on a2ap-dgx037. The terminal collector verifies frozen payload hashes and reports STATIC_TOPOLOGY_CAPTURE_PASS. The retained [raw report](collected/222412.pbs111/runs/222412.pbs111/topology.json), [collection receipt](collection.json) and [structured review](locality-review.json) distinguish evidence validity from scheduler completion.

The process was allowed logical CPUs 28–41 and 140–153: 28 logical CPUs, representing 14 cores with SMT, all on NUMA node 0. The allocated H100 UUID ends in 2ff560f0eaa3, PCI 0000:c3:00.0. Its sysfs NUMA node is 1 and its local CPU list is 56–111,168–223. **The allowed mask has no overlap with that GPU-local CPU list.** NUMA describes CPU and memory locality: CPU work or host memory on the other socket may need an inter-socket path, but static placement alone does not establish a measured cost.

The visible NVML index is 0 within this allocation. It is not evidence that this is the node's physical GPU zero or the same ordinal as a full-serving rank. The topology matrix contains one visible GPU and NIC connectivity, not a complete eight-GPU NVLink matrix. Its CPU-affinity cell is blank; the conclusion above uses the explicitly collected process mask and sysfs lists.

This probe loaded no model and measured no TTFT, ITL, goodput, GPU utilisation, worker CPU demand, memory placement or saturation. Those fields are not collected, not zero or healthy. A one-GPU/14-core allocation can have a different cpuset from a two-node/16-GPU serving job. It does not prove that existing serving bindings are remote, that CPU scheduling is the bottleneck, or that NUMA-local binding will improve the contest score.

The current wrapper selects worker CPU ranges by ordinal offsets. The next derived full-serving bundle should record each worker's actual allowed mask, rank, GPU UUID/PCI identity, and CPU/NUMA intersection on both nodes without changing binding. Only if that confirms an actionable mismatch should a separate bounded, controlled affinity comparison be prepared. Never request CPUs outside the scheduler cpuset or change frozen queued payloads. Existing score/profile/protocol and output gates remain mandatory; account for monitoring overhead.

PBS reports **78 seconds**, corresponding to **2.773333 SU** at one GPU × 128 SU/GPU-hour. The published ledger delta already reconciles this charge; do not charge or reserve it again. The original three-minute ceiling was 6.4 SU. No new allocation was submitted for this review.

[NVIDIA's topology reference](https://docs.nvidia.com/deploy/nvidia-smi/index.html#topology) explains the static affinity fields. Earlier pending/awaiting-collection descriptions in RESULTS.md and the journal remain dated historical records, superseded by this terminal review. No performance improvement or official accuracy certification is claimed.
