# Source selection and inherited metadata

The authoritative runtime selector is run.py: A labels select the accepted Scotch source; B labels select `initialized/order-zyx`. The separate accepted-source-manifest.json and accepted-zyx-source-manifest.json bind 1,040 initialized files each. Full source hashes are checked inside the compute allocation before and after all measurements; per-method canonical input validation and field/copy integrity gates are independent.

source-observations.json is inherited from the earlier H/S helper. **Only its S entry is consumed**, by verify-inputs.py for Scotch. Its H entry refers to the historical original xyz source and is not the candidate source or an execution instruction. The zyx candidate is checked by case_checks.source_check(..., 'zyx') and its own accepted manifest. This distinction is intentional and is also confirmed by the live text-only site preflight; no old xyz input is silently substituted.

The source manifests and canonical pins are preserved from reviewed predecessor work; the live preflight reads only small source text inputs, not a full mesh/field hash on the login node. Heavy inventories and actual solvers belong inside the scheduled allocation. Method-specific initialized meshes/fields differ, while the original mesh, physics and canonical source are fixed.
