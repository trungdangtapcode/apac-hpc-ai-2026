# Actual H200 prefill-interaction submissions

The frozen two-run plan and inverse-diff/syntax/hash checks passed before submission. The live queue under the shared lock had room for both jobs, without cancellation or modification of 24928/24962. Each returned job ID was recorded immediately, then the registry and prepared plan were updated.

| Job | Role | Fixed deployment |
|---|---|---|
|24964|Fresh observed DeepGEMM prefill control|N60, chunk8192, HPC-Ops decode|
|24965|Observed HPC-Ops prefill candidate|N60, chunk8192, HPC-Ops decode|

Both are pending for Resources in the retained 05:38 UTC scheduler snapshot. There is no performance result yet. Four own H200 jobs are active: old receive2 24928, exact N62 repeat 24962 and this pair. This stays below the five-job cap. Each new allocation is 16 H200 for at most 17 minutes, with complete raw 60/120/30 and output checks; no PBS SU is reserved.

[The plan](PLAN.md) explains prior measured H200 cases, the new missing interaction, the actual pinned HPC wrapper, a one-factor matched comparison, required runtime/output/telemetry review, the 1% descriptive advancement threshold and independent confirmation requirement. The candidate is not claimed to improve on the incumbent before it runs. No N64 growth, closed-branch retry, numerical shortcut, job-script promotion, organiser upload, authentication restart or background AI was performed.

The new resource inspector and two completed observer reviews are retained in ../research-followup-20261020-0530/. PBS access remains unavailable because no live VPN session was found; published credit/remote results remain at their older timestamp and prior reservations remain intact.
