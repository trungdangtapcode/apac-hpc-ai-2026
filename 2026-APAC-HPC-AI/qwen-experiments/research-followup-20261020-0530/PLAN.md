# Independent N62 confirmation and observer review

The accepted H200 N62 result 24915 reaches 3022.035 good output tokens/s, 4.537% above fresh auto N62 control 24914, but has only one treatment observation. Independently reproduced N60 results and the new unobserved N60 job 24926 = 2991.709 support reproducibility at the lower load. The observed N60 control 24927 = 2971.312 is 0.682% below its unobserved partner in one pair; this does not establish a significant overhead or erase the N62 uncertainty.

Submit exactly one independent N62 repeat, derived byte-for-byte from 24915's submitted payload except experiment names/config provenance/checksums. Preserve all benchmark execution files, kernels, numeric formats, workload, load, transport and post-score diagnostic. No new knob or automatic N64. Full local raw protocol/output/runtime/SLA gates and independent repeat comparison are required; official accuracy stays unverified.

Bound: one two-node, 16-H200 Slurm allocation, 17 minutes maximum, no PBS SU spending. Check the live queue under the shared watcher lock and remain within five active H200 jobs. Existing 24928 keeps its queue position. PBS access currently fails because no live VPN session exists; do not infer terminal status or credit from old snapshots, do not submit PBS, and do not restart authentication as part of this step.

Inspect all new observer artifacts for role/UUID mapping, phase coverage, errors, unsupported fields, clocks, resource samples and observer cost. Compare interval2 only against the observed interval1 control after it completes. A flat/loss closes that setting; a repeatable useful gain warrants a controlled confirmation rather than blind interval growth.
