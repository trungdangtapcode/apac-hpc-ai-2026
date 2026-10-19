# Status check — 19 October 2026, 11:45 UTC

H200 jobs 24733, 24736, 24737 and 24738 remain pending. The displayed reason changed from Priority to Resources. Both hpcai nodes remain allocated, so these jobs have not received their required allocation. This reason alone does not establish queue rank, an estimated start time or a scheduler failure.

The PBS queue remains empty. Existing VPN/SSH access works without restart or authentication. The ledger at 19/10/2026-19:40:02 SGT reports Used 29391.644 SU, Balance 34608.356 SU and In Doubt 0. No new result, submission, charge or research decision was made in this check.

Best locally accepted observations remain H200 2938.628 and H100 2430.891 good output tokens/s. The H200 interaction repeat has not run. The H100 N56 load trial had no observed gain and forced prefill Tree regressed; retain those conclusions from [the completed-result review](../status-review-20261019-1111/RESULTS.md). Official accuracy remains unverified. Preserve existing H200 queue positions.

Raw snapshots: [Slurm queue](slurm-queue.txt), [accounting](slurm-accounting.txt), [nodes](slurm-nodes.txt), [PBS access and credit](pbs-status-credit.txt). This is a dated observation.
