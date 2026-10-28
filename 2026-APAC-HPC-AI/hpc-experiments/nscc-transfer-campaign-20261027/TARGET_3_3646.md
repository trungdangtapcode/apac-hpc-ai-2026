# Beat the reviewed NSCC result

The target is **less than 3.364622070 seconds per solver step on NSCC ASPIRE-2A**, the reviewed result from our job 25940700. It is a reproduction of the main organizer recipe, not a new optimization. Iris seconds are not substituted for NSCC measurements.

## Next measurement

The first executable trial is already frozen: **Scotch control, hierarchical xyz, hierarchical zyx**, all on the same four-node allocation with 512 MPI ranks. Each arm independently performs complete mandatory preparation and 150 solver steps. The mean includes all 149 native timed intervals, including slow steps. The maximum request is 90 minutes, or 768 SU at the previously verified rate; current rate, credit and all existing commitments gate admission.

The hierarchy pair uses factors **(16 8 4)**. Changing order is a native Basic configuration change and does not require the optional pinning library. The Iris full run favored zyx by 21.2371%, which motivates this test but does not predict an NSCC speedup. The old shorter and cross-allocation results do not replace a fresh control.

## How a result will be judged

A candidate needs a complete, valid run: prescribed mesh, precision, fixed work, initialization, hosts and ranks; all command exits zero; 150 ordered solver steps, 149 matching native timings and finite force coefficients. Preserve original source, payload, runtime, output and terminal scheduler evidence. A timeout or an error is retained but is not a completed measurement.

Report two separate comparisons: whether the candidate mean is below the historical 3.364622070 target, and whether it beats the fresh Scotch control in the same allocation. A new low Scotch repeat alone is not proof of a tuning gain. Inspect median, P95, maximum, all slow steps, resource evidence and numerical output alongside the mean.

Keep the full drag-coefficient trajectory. The native Basic rules and the Bonus injection accuracy requirements are different. Do not import a Bonus tolerance as an invented Basic gate, and do not describe a finite but changed output as numerically equivalent. The Iris full pair's final Cd differs by 1.6185%; that limitation remains visible.

A promising hierarchy result gets a reversed-order full comparison, followed by independent full winner repetitions. Report allocation and node variability; do not pool individual serial steps as independent experimental repetitions. A target hit is a local measured result, not an official contest score or a robust universal speedup.

## If the native order branch loses

Close unchanged losing configurations and review the separate placement branch. Actual Pstream integration and mapping qualification gate that branch, not the native hierarchy tests. Balanced versus aggressive rank placement and alternative hierarchy factors remain distinct conditional hypotheses in PLAN.md. Do not submit combinations without evidence for their components or blindly fill the queue.

## Current access and execution boundary

On 28 October 2026, one initial authorized VPN recovery and three additional owner-requested attempts returned Authentication failed before SSH/PBS. Phone-side DUO delivery or approval is unknown. The owner's phone does not hold DUO; do not ask them to inspect it. The retries were bounded and private authentication state was preserved. No current NSCC queue, balance or new submission is claimed.

The 23 October access note records an SSH warning that the account password would expire in three days. This is an unresolved troubleshooting lead, not proof of an expired current credential or the cause of the VPN rejection. No password change or reset was attempted. Do not diagnose every generic authentication failure as a DUO problem.

Job 2294262 continues on Iris under its existing reservation and one-active-allocation cap. Preserve it while NSCC is unavailable. Before NSCC submission, refresh both CPU and AI queues, project credit, old job provenance and commitments under the required locks. A definite scheduler receipt is required to say submitted.
