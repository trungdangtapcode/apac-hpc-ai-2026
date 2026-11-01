# Collated I/O: positive first pair, not confirmed

Job 2294634 completed 0:0 on iris001, 2,738 seconds, 56 CPUs. Independently verified 116 selected file hashes and both complete 40-step / 39-interval native outputs. Same initialized Scotch source, same socket/core MPI command, unchanged fixed work, physics and function objects. Only file handler differs.

| Arm | Mean s/step | Median s/step | Maximum s/step | Cd at 40 |
|---|---:|---:|---:|---:|
| Default I/O, first | 31.600735680 | 31.271388431 | 35.908385101 | 0.436959331 |
| Collated I/O, second | 29.681757101 | 28.687821001 | 51.401735539 | 0.436959331 |

Collated mean is **6.072575648% lower in this allocation**. All 40 Cd rows are exactly equal; source/copy inode isolation, time-zero field seals, native iteration counts 15/12/8/8, actual I/O headers, native wall-clock file and runtime identities pass. Native sample recommendations 15/192 versus 39 observations qualify the second arm. Preserve its 51.4017-second sample; no outlier deletion.

Both arms have timing trends. INSPECTION.json records first 10 / last 10 means, population SD, nearest-rank P95 and GNU time counters. The collated second arm progressively accelerates; treatment and time remain confounded. The mean difference is not a verified optimization, NSCC improvement or Gadi reproduction. No hardware bandwidth, CPU frequency or actual solver helper affinity was collected. Node procfs and command-level resources are inspected; they do not establish why the trend occurred. No native fatal marker or scheduler stderr was observed.

Cost 42.591111 CPU-hours, conservatively counted 43; retire the 70-hour maximum once. Local consumed allowance becomes 560 CPU-hours, reserved 0, previous internal stage 587. Next: reverse order collated then default before promoting a gain. A separate default-versus-socket mapping hypothesis is prepared but deferred; do not spend on it before this confirmation.
