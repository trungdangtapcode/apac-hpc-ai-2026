# MPI-rank policy qualification actually submitted

Scheduler accepted **2294801** at 2026-11-04T17:22:17.718827Z. This is a distinct no-solver diagnostic after unchanged copy/hash policy failed independent confirmation. One exclusive Iris node /56 CPUs /zero GPUs /low QoS /maximum 5 minutes reserves 4.666667 allocated CPU-hours, entirely within the current 1,210-hour internal stage (1,175 consumed). No owner-limit increase or billed-SU assumption.

Each arm starts 56 MPI ranks under inherited versus launcher interleave policy. Each rank records actual policy, allowed masks and first-touch page counts for an isolated anonymous 8 MiB region. Guard pages prevent accidental VMA merging; ambiguous page accounting fails explicitly. This measures mechanism availability and observed page distribution, not solver performance or per-rank solver behavior. No input mesh, sampler, native solve or speed score is involved.

Local syntax/resource/hash checks pass. A local synthetic-rank test could not run because this login machine lacks numactl; the failure is retained, not presented as a placement pass. Iris already qualified numactl availability in earlier preparations, but this actual 56-rank code still needs terminal review. Offline checks regenerate the initial hash list; run them only before sealing, never against a frozen submitted deployment. Preserve the exact frozen five-file runtime manifest.

Receipt and post-submit scheduler snapshot are separate. Review 112 per-rank records, both MPI exits, exact mapping accounting, policy propagation, masks, hashes and terminal accounting before interpreting the mechanism. A successful diagnostic alone cannot establish a solver gain.
