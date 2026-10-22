# 22 October: independent full N64 replication

Recorded 2026-10-22T00:31:33.184741+00:00. The accepted full N64 point 25366 improves the fresh observed full N62 control by 1.082867%. This exceeds the 1% confirmation gate but has only one full N64 deployment. The next question is repeatability, separate from the exploratory N68 screen.

The frozen bundle `s34-h200-observed-n64-full-repeat` copies all operational bytes from the submitted N64 candidate. Only job identity and provenance differ. It retains full 60/120/30 timing, N64, source precision, backends, topology, cold workload and resource observation. CPU AST/shell checks and all 17 payload hashes pass.

One 16-H200/two-node allocation is bounded at 17 minutes, with no PBS SU. Source review, partition and queue checks precede a single submission. Report both full N64 measurements and their variation before considering submission-primary promotion. Require local protocol, SLA and output gates; official accuracy remains unverified.
