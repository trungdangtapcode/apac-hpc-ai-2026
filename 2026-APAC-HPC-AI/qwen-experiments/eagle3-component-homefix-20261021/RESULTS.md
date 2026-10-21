# Writable-cache component repair submitted — 2026-10-21T03:46:50.645252+00:00

Definite **222729.pbs111**, initial state **R**, one H100 / four minutes / maximum 8.533334 SU. [Receipt](pbs-receipt.json), [scheduler state](post-submit.txt), [exact repair and gates](PLAN.md). The preceding allocation left the queue before this fresh qsub, so no dependency was needed; the adapter also supports a verified afterany dependency if only that known predecessor remains active. No overlapping allocation, uncertainty retry or native payload mutation occurred.

Actual /generate synthetic forwarding passed in 222722; the following metadata/tensor stage stopped during imports because FlashInfer attempted to use read-only HOME. This repair explicitly places HOME/cache inside the existing private /tmp bind; the diagnostic Python scripts remain byte-identical. Actual repair success, native config/tensor checks, model loading, PD transfer and speedup are not claimed at submission.

Fresh locked ledger: Used **43575.143 SU**, Balance **20416.324 SU**, In Doubt **8.533 SU**. The 222721 charge now uniquely reconciles; 222722 remains unposted and retains its maximum together with this job, total 17.066667 SU. Internal headroom is **7407.790333 SU**, under the same 51000 cap / 13000 buffer. [Command-scoped queue/accounting/credit](pre-submit-commands.json), [reconciliation](reconciliation.json). H200's five positions remain untouched.

## Terminal review — 2026-10-21T04:45:42.238481+00:00

F / exit 1; 64 seconds, estimated 2.275556 SU. Gateway passes; imports pass with private HOME. UUID/name assertion fails before values were retained. No native config/tensor result or model load. [Review](REVIEW.md).
