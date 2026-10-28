# NSCC target, access attempts and partial order confirmation

Recorded 28 October 2026, Vietnam time (UTC+7). This is an HPC execution checkpoint, not a new performance result or submission.

## Objective and control

The owner asked to continue until the reviewed NSCC mean of 3.364622070 seconds per step is beaten. The frozen native first wave remains the appropriate direct measurement: four nodes, 512 ranks, default Scotch followed by hierarchical xyz and zyx, each with complete preparation and 150 solver steps. It compares a fresh Scotch control with the order candidate on NSCC; it does not apply an Iris percentage as a forecast. The independent admission audit found no identified new payload defect and confirmed that PMPI integration is not required for these native Basic trials. Real three-arm runtime remains unmeasured.

## Actual access attempts

CPU SSH reuse returned no live VPN. One authorized recovery at approximately 16:16 returned Authentication failed before SSH/PBS. The owner then clarified that DUO belongs to the captain, not their own phone, and explicitly requested additional attempts. Three bounded attempts at 16:19:19, 16:19:43 and16:20:08 each returned Authentication failed after approximately 4.5 seconds. No live tunnel resulted, no password change was attempted and private authentication state was preserved. Phone-side delivery and approval are unknown. Research records contain only classified outcomes, not credentials, terminal authentication output or session state. No indefinite loop or schedule was started.

The 23 October access note records an SSH account-password expiry warning for three days later. That is a plausible lead to resolve, not proof that the current VPN failure has this cause. The generic rejection also does not prove that DUO was denied or that a push arrived.

The real admission precheck at 16:21:05 returned BLOCKED before CPU qstat. Thus neither current queue nor project balance is known, and old job ownership/reservations remain unresolved. No new NSCC deployment, reservation, qsub attempt or scheduler job ID exists. Those facts must remain explicit.

## Ongoing accessible measurement

Iris 2294262 remains RUNNING on iris005 under its existing 168-CPU-hour maximum reservation. At16:21:35, xyz had reached Time 107/150 with 105 completed timing intervals and no observed fatal marker; zyx had not started. The last five intervals were 21.20–21.56 seconds, without a completed full mean.

A bounded local reinspection of parent 2294234 showed xyz timing windows of 29.1406 seconds (first 50), 26.4399 (middle 50) and 25.2467 (last 49), compared with zyx 21.1404/21.2848/21.2643. This highlights within-run variation in the parent xyz arm and supports the importance of finishing the reversed full comparison. Do not extrapolate a handful of new intervals into a confirmed speedup, numerical equivalence or a hardware diagnosis. Parent final Cd difference remains 1.6185%.

## Decision, spending and remaining blocker

Keep 2294262 and its position; one own Iris allocation occupies the cap. No additional Iris reservation or NSCC SU charge was created. No accessible, authorized additional trial fits current caps: NSCC admission is blocked at access and Iris is occupied. The explicit next NSCC action after verified authentication is fresh queues/project/old-job reconciliation under CPU-before-AI locks, then reviewed deploy and one-shot submission if all gates pass. The first trial's request ceiling is 768 SU at the previously verified rate, subject to fresh verification. Do not wait on an optional pinning investigation to run it.

[TARGET_3_3646.md](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-transfer-campaign-20261027/TARGET_3_3646.md) records target-hit versus matched-improvement criteria and followup decisions. Raw safe retry outcomes and precheck JSON are retained in the campaign. The live Iris phase snapshot is retained in its derived bundle. No AI queue, budget or payload and no submission materials were changed.
