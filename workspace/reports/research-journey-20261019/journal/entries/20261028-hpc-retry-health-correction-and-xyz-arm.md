# Correct VPN readiness and assess the first reversed arm

Recorded 28 October 2026, Vietnam time (UTC+7). This is a retry and partial research checkpoint, not a new NSCC submission or a completed matched result.

## Actual retry and correction

The owner requested another attempt. A temporary helper reported live VPN solely because a namespace-entry command succeeded. That is a false-positive readiness test: the namespace can exist before authentication succeeds. Immediate CPU SSH failed before reaching the host and the client exited with Authentication failed. The user-facing success claim was corrected immediately; the original machine record retains its historical value and correction.

A read-only transport probe now separates namespace, tunnel IPv4, reachable SSH service and authenticated SSH access. Six regression tests cover the false-positive state and avoid claiming authentication from a banner. Two further authorized attempts with the stronger probe also failed. Only classified outcomes were preserved, with private caches left untouched. The pinned client-source review does not establish the rejection's root cause or DUO phone delivery. See [access correction](../../../../notes/vpn-access-20261028.md) for exact limits and primary sources. No new NSCC reservation or job ID exists, and both real PBS queues and current credit remain unknown.

## First-arm observation on Iris

Job 2294262 remains running on iris005. At 16:38:43, the first arm, xyz, had completed 150 steps and 149 native timed intervals. The batch's arm gates passed. Its mean was 21.823903674 seconds per step, median 21.380753585, P95 21.743312887 and maximum 70.992053237 at Time 3. The mean retains that slow interval and every other prescribed sample. All 150 total Cd rows exactly match the retained xyz rows from job 2294234.

The same configuration's prior mean was 26.953798643 seconds. Its 19.0322% lower repeat mean is not evidence of a new optimization: node and serial execution order changed together. This strengthens the need for the current matched zyx second arm before treating the earlier 21.2371% difference as stable. Numerical repeatability of these total Cd rows does not prove full-field equality, and timing variation does not reveal its physical cause.

## Gates and next decision

This first-arm assessment uses runtime summaries and retained row arrays. Independent full raw-output replay, final source/library stability, terminal scheduler state and complete-pair review remain pending. Do not retire the 168 CPU-hour reservation early or call a partial pair finished. No additional CPU credit was reserved.

Keep the one active Iris allocation. There is no additional eligible submission while NSCC is inaccessible and the Iris cap is occupied. Once NSCC access is genuinely restored, the ready native Scotch/xyz/zyx trial stays first; it does not wait on PMPI diagnostics. At Iris completion, collect both full native logs/tables, compare the order effect to the parent, preserve every tail and output difference, and reconcile actual resources once.

Evidence: reverse bundle `arm-status-20261028T0938.json` and `first-arm-assessment-20261028.json`; classified retry records in the NSCC campaign launch directory; `nscc_vpn_path_check.py` and its regression tests. No frozen submitted payload, AI queue/budget or submission materials were changed.
