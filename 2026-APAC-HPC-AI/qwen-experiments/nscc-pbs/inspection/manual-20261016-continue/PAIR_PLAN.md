# H100 fresh control and MNNVL replication — 16 October 2026

User explicitly requests additional GPU submissions now; Codex autopilot stays off.
Source terminal sweeps 220720/220721/220722 pass sealed payload, full protocol,
short nonregression and 12/12 long retrieval diagnostics. Review files retained.
MNNVL improves historical N32/N34 goodput by 7.77/7.90%; standalone FlashInfer
is 1.79/1.40% lower at those loads. Prefetch is 0.29/0.17% lower; it is not selected
as an inference improvement. Startup effects remain confounded by cache/nodes.

Old per-role logs are empty. Live server-info for 220720 reports MNNVL and the
expected TP/EP/transport, but eight-rank initialization/effective KV dtype remain
unresolved. This pair explicitly corrects observation and measures replication;
it does not claim the old runtime gate passed. Update the earlier conditional
confirmation plan: identical already CPU-validated task-side logging on both
new allocations is the bounded way to resolve missing runtime evidence while
measuring. No separate logging-only allocation and no candidate promotion.

h100-control-07: unchanged control worker from load-sweep-03.
h100-mnnvl-repeat-08: unchanged MNNVL worker from h100-mnnvl-04.
Both use the same long diagnostic, compute-task logging, model/images, topology,
RR/NIXL, graph sizes and full 60/120/30 closed-loop 4000/200 protocol.
Planned loads 32,34,36,38,40,42; stop increasing upon failed SLA/error gate.
Do not add N44/N56 or enable automatic retries. Keep raw failed-SLA points.
Pair validation verifies all execution files identical apart from MNNVL worker;
config metadata and bundle path/job names differ intentionally.

Reserve at most 3072 SU under budget.lock before submission; refresh all own
queue and myprojects. First job from empty queue; second afterany first, max one
running 16-GPU job, below cap3. Campaign cap16384SU, project reserve13000SU.
Record each returned job ID before further submission; uncertain outcome retains
reservation and blocks blind retry. Upload remote checksums already passed.

After completion compare N32/N34 against fresh and historical control; retain
all loads/SLA/TTFT/ITL/drift. Inspect task logs for eight-rank backend, resolved
ServerArgs/KV, NIXL and pair warmup. Missing logs, output regression or deferred
long checks block confirmation. Synthetic checks do not establish organiser
99% accuracy. No automatic third successful repeat planned.
