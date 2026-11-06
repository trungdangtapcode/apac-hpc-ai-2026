# Failed six-arm comparison: proof-log parser false-negative

**2294920 FAILED 1:0**, 6,575 seconds /56 CPUs /iris001. Five native arms complete 40 steps and 39 intervals; T2 never ran. The complete six-arm measurement is invalid. Recovering diagnostic records does not change scheduler state or supply the missing solver and source/runtime-after gates.

| Completed arm | Mean (s/step) | p95 (s/step) | Maximum (s/step) |
|---|---:|---:|---:|
|T1-teammate56|33.592853770|35.877385906|40.429614739|
|O1-original48|24.781383192|25.580773512|27.208364013|
|H1-hybrid48|34.849654258|35.504586188|35.509746260|
|H2-hybrid48|29.897147666|41.066359576|42.249923362|
|O2-original48|24.714025046|25.470522712|26.578287902|

All 301 retained file hashes verify. Root and independent replay pass the five native work/output/field gates. Payload and accepted source-before gates pass; source/runtime-after and final six-arm checks were **not reached**. All five telemetry streams are present; pressure is unavailable. RSS is a process collector, not summed MPI memory. No bandwidth or causal bottleneck profile was collected.

The final rank probe returned zero but our prefix-dependent stdout parser read 55 records. Diagnostic JSON recovery finds all 56 unique ranks and nonoverlapping CPU masks on iris001; rank 28 lost its prefix when concurrent stdout was interleaved. This is an agent-owned logging/validation bug. The fix is exclusive per-rank proof files with strict count/schema/affinity verification, qualified by a small MPI-only job before another long measurement. Existing submitted payloads remain frozen.

The original48 arms (24.781383192 /24.714025046) are both below the combined mapping+collated arms (34.849654258 /29.897147666). These are **partial diagnostic contrasts**, not a certified matrix ranking. They justify not repeating the unchanged combination. Next candidate keeps the successful default48 mapping and changes only its file handler to collated, alongside O48 and actual teammate56 controls. This isolates the I/O change and keeps absolute seconds primary; historical 22-second observations remain unbeaten.

Actual cost is 102.277778 allocated CPU-hours, conservatively 103. The 224-hour maximum reservation retires once: **1,499 consumed /zero reserved /1,620 internal stage**. Site-billed SU is unknown. A new protocol qualification and any R2 native admission require their own receipts, gates and reservations.
