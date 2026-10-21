# Queue parser correction before any allocation

The initial adapter combined own-queue output, historical qstat -xf records and project credit, then searched all text for job rows. A wrapped historical Submit_arguments line began with 551.pbs111 benchmark.pbs, causing a false active-job match. The adapter stopped before reconciliation, reservation or qsub. Original stdout/stderr and source accounting are retained; no uncertain job or extra cost was created.

The corrected adapter keeps each remote command's argv, return code and output in structured JSON. Only qstat -u stdout enters active-job parsing. Ledger/accounting text remains available separately for existing reconciliation. The retained failure reproduces the false match; syntax and corrected scope checks pass.

Because the upload had already succeeded, an explicit resume proof verifies the unchanged local and remote SHA256SUMS digest and every payload file. It also verifies no receipt, reservation or uncertain submission exists. The corrected adapter rechecks that proof, then obtains fresh queue/credit state under the budget lock. Frozen native payload and acceptance gates are unchanged. Never repeat an uncertain qsub or overwrite an existing remote payload.
