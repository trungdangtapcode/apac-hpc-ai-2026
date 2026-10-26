# 26 October: select zyx from fresh controls and preserve raw cuts

The four native cuts in job 2294097 completed 0:0 in 363 seconds. Full current canonical mesh checks pass before and after; 51 archived artifacts replay with matching hashes. Each order has 56 partitions, 65,334,765 cells and 336 restored fields.

| Order | Interface faces | Largest rank face count | Maximum neighbors |
|---|---:|---:|---:|
| xyz | 1,326,716 | 93,343 | 14 |
| xzy | 1,256,287 | 98,522 | 12 |
| yxz | 1,364,407 | 99,311 | 12 |
| zyx | 1,269,961 | 91,721 | 13 |

Select zyx as a hypothesis: all three communication proxies improve over the fresh control, while cell imbalance remains below 0.0004%. Xzy improves totals and neighbor count but increases the largest rank's face count, so retain it as a tradeoff. The previous Scotch loss shows that static counts do not establish speed. No solver winner is claimed. [Full native result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/iris-hierarchical-order56-r2-20261026/completed-2294097/RESULTS.md).

Three serial tools overlapped after the memory gate passed; batch MaxRSS was 96,223,076 KiB. This is resource evidence, not memory bandwidth or a ranked runtime. The six-minute allocation estimates 5.646667 CPU-hours; retire only its own maximum and retain a rounded six-hour allowance.

Job **2294098** clones fresh xyz and zyx into separate initialized trees, verifies content and inode separation, then runs renumberMesh, potentialFoam and applyBoundaryLayer with the unchanged numerical inputs. It captures source, initial-field and current serial-mesh hashes before and after, verifies original cuts were preserved, and creates each READY only after its checks. The job has one exclusive 56-CPU node and a 40-minute maximum, 37.333333 allocated CPU-hours. At 13:41:44 UTC it was RUNNING on iris001; both-case completion was pending.

The Iris envelope remains 224 hours. Consumed planning allowance is 129 hours and this reservation brings commitment to 166.333333 hours. Review actual initialization cost before selecting the next matched solver screen. Do not silently raise the envelope or claim the unfinished cases complete. NSCC's separate trace job 26004608 was still Q/q5 for node_pool at 13:41:43 UTC.

All source, receipts, raw archives, failed branches and interpretation changes are preserved in small explicit Git checkpoints. No authentication material is included.
