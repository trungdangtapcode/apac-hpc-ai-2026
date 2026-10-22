# N64/N68 short-screen submission

Job **25371** was definitely submitted after the full N64 review passed. The immutable bundle is `s31-h200-n64-n68-screen`: 16 H200 GPUs across two nodes, maximum 17 minutes, no PBS SU. The submission receipt, partition check, source accounting, and immediate queue snapshot are retained beside this report.

The same observed deployment measures N64 then N68 with 20-second warmup, 40-second measurement, and 30-second grace. All execution files other than job identity/configuration are unchanged from the source. This is an unranked screen. Dense decode graphs still stop at batch 64; client concurrency 68 does not establish actual decode batch 68 or graph support above 64.

Require zero request errors/cancellations, joint SLA fraction at least 0.90, passing local output checks and at least 1% goodput gain against its own N64 control before considering a fresh full N68 pair. Official accuracy remains unverified. The immediate queue state is a dated snapshot, not a live claim.
