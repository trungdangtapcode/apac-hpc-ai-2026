# Four native hierarchical cuts completed

Job **2294097** completed 0:0 on iris005 in 363 seconds. All four cases have 56 partitions, 65,334,765 cells and 336 restored initial field files. Full canonical serial-mesh hashes match before and after, and all 44 kit files pass their source checks. The 51 archived artifacts match their hashes and lengths.

| Order | Unique interface faces | Largest rank interface count | Maximum neighbors |
|---|---:|---:|---:|
| xyz, fresh control | 1,326,716 | 93,343 | 14 |
| xzy | 1,256,287 | 98,522 | 12 |
| yxz | 1,364,407 | 99,311 | 12 |
| zyx | 1,269,961 | 91,721 | 13 |

Select **zyx** for the next measured hypothesis: total interface faces are 4.28% lower, the largest rank count is 1.74% lower, and the neighbor maximum is lower than the fresh control. Cell-count imbalance remains below 0.0004%. Xzy has fewer total faces but a worse maximum rank face count, so retain it as a tradeoff rather than initialize it automatically.

These are structural measurements, not solver speedups. The prior Scotch result showed that a lower total interface count can still run slower. Initialize fresh xyz and zyx together, preserve the original cuts through independent copies, and then make a controlled solver comparison. Neither case is READY or solver-qualified yet.

The new xyz counts match the old control summary, but count agreement does not retrospectively establish the old serial mesh's byte identity. Future comparisons can now use the fully checked fresh control.

Three serial workers overlapped after measuring 182,694,584 KiB MemAvailable. Slurm reported batch MaxRSS 96,223,076 KiB. These are resource observations; no memory bandwidth or kernel counters were collected. Concurrent cut durations are unranked.

The allocation estimates 5.646667 allocated CPU-hours. Retire the 37.333333-hour maximum once and retain a rounded six-hour allowance. Iris now retains 129 consumed planning hours before the next admission, within the 224-hour envelope. No SU charge is inferred. Replay with `python3 replay.py`.
