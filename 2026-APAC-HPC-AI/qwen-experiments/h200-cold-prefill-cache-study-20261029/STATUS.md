# Actual cold-cache pair accepted

Observed 2026-10-29T21:45:47.454741+07:00, Vietnam time (UTC+7). Slurm accepted **27376** as the fresh native RadixCache control and **27378** as the prefill-only ChunkCache candidate. These are submitted full N64 trials, not measured improvements. Cap64 job 27365 remains independent.

Each job uses 16 H200/two nodes/17 minutes maximum, 4.533334 GPU-hours; pair maximum 9.066667, no PBS SU. Admission preserved own cap 5 and existing positions under the lock, with fresh queue, frozen manifests, sbatch validation and definite receipts. Prepared source/configuration and 22 meaningful CPU fixtures are captured in 248a201d.

Only prefix cache selection changes on the two prefills. Physical KV remains, decode cap 256/polling 1 and all other model/workload/source/runtime/KV/semantic/output gates stay. Require all-rank native flags/classes, both semantic routes and complete local output evidence. Compare full valid runs against fresh 27376, require >1% useful gain and acceptable tails before independent confirmation, otherwise close unchanged. Official accuracy remains UNKNOWN.

Current observed queue is recorded below. States are dated snapshots; query actual scheduler before acting.

                 JOBID                     NAME    STATE       TIME  NODES NODELIST(REASON)
                 27378         ap42-s104-pcache  PENDING       0:00      2 (Resources)
                 27376           ap42-s103-ctrl  PENDING       0:00      2 (Resources)
                 27365         ap42-s102-dcap64  RUNNING       8:00      2 g[1,4]

Raw receipt/reservation directories retain exact time and manifest. HPC, submission, authentication and disabled background automation stay unchanged. External object bytes are not uploaded by Git.
