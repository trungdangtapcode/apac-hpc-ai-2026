# CPU queue policy: correction after reading actual routing

Read-only PBS snapshot at 2026-10-21T19:53:00.688157+00:00 is retained in queue-policy-snapshot.json. `normal` is a routing queue; it can send jobs to q1–q6, qlong/qdev and GPU queues according to resources and site policy.

The earlier assumption that qdev's overall 256-CPU limit might prevent every larger contest job was too broad. **qdev also limits each job to 128 CPUs.** A 256- or 512-CPU request through normal therefore requires another destination; q5 publishes a 2,048-CPU per-job maximum and 24-hour maximum, while q6 allows larger jobs. Do not submit multi-node work directly to qdev or bypass project restrictions. Continue using authorized `normal` and inspect the actual routed job/receipt. Queue visibility alone does not certify immediate scheduling or all account permissions.

The qdev aggregate limit still explains waits for our one-node requests. It does not describe total cluster capacity. New two-node/four-node jobs can follow the normal route and must be verified after real submission. We have not yet run a multi-node CPU job in this phase. No private ACL identities or authentication state were captured.
