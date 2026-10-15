# Continuous optimization campaign —2026-10-15

User instruction: continue and use available time/GPU. Commissioning baseline
220562 succeeded. We move to a bounded **16384SU total campaign**, including
previous usage, maximum16GPUs on NSCC, one PBS GPU job at a time, project reserve
at least13000SU. Budget changes are recorded in `nscc-budget.json`.

## Avoid repeated model startup

Baseline required about20minutes startup and23m33s overall for one point.
Job **220575.pbs111** runs one45minute allocation and measures
**N32,34,36,38,40,42** with the unchanged official60/120/30 protocol at each point.
N32 repeats baseline; subsequent loads run only while previous SLA/error gate
passes. Insufficient remaining time is explicitly deferred. It reserves1536SU;
actual charge depends on allocated runtime, not the number of points attempted.

Frozen bundle: [load-sweep-03](load-sweep-03/).
[Validation](load-sweep-03-validation.json).

## Prepared next trials

1. [h100-mnnvl-04](h100-mnnvl-04/): change decode collective fusion toMNNVL.
2. [h100-flashinfer-05](h100-flashinfer-05/): change decode attention toFlashInfer.

Both were uploaded with all SHA256 checks passing; neither was submitted when
this plan was written. GPU compatibility, performance and accuracy are unproven.
Each uses the same load grid/protocol and maximum45minutes. The backend winner
on H200 is a hypothesis for H100, not a result on H100.

After current job completes, collect all exports and reconcile credit. A complete
passing N32 point with no errors/cancellations and no newly failed short-output
cases allows the next independent backend pilot; a higher load failing does not
invalidate a passing lower load. Submit only one own PBS GPU job at a time.

Separate12-case ~3800-token concurrent retrieval diagnostics follow performance
when sufficient time remains; failed or deferred checks must be explicit. These
do not replace organiser accuracy, prove99%reference, or establish full PD
equivalence. Keep all raw prompts/responses, failures, client logs and checksums.

## Work while GPU queues wait

- Inspect prefill weight-loading latency851s; compare actual loader/thread/CPU
  placement and storage behavior against decode before choosing an isolated fix.
- Prepare losslessEAGLE3 and separatevLLM branches from inspected primary sources.
- H200: keep confirmations23839/23859 and new interaction pilots23904–23906.
  SharedSlurm cap5; existing higher-load gates remain unchanged.
- Wake schedule now checks every5minutes and triggers model work on state changes;
  transient quota errors back off30minutes. Reports are in
  `/home/apacsc42/workspace/research-autopilot/LATEST.md`.
