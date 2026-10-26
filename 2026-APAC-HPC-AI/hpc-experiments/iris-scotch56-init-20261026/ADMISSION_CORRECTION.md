# Reviewed pre-submission assertion failure

The first initialization admission did not reach sbatch. Its accounting assertion expected a trailing pipe, but Slurm parsable2 output ends after the last nonempty field. The root's read-only inspection on the actual Iris login found no remote submit intent or receipt and no own tu- job. The cut accounting is still COMPLETED / 0:0 / 56 CPUs.

Preserve the original local intent and its single 18.666667 allocated CPU-hour reservation. The explicit resume-submit action requires this reconciliation, rechecks the live queue, exact payload hashes and accounting, and uses that existing reservation. It does not delete the guard or allocate a second reservation. The remote exclusive intent still prevents a duplicate sbatch.

The corrected parser compares complete fields rather than a delimiter substring. This is an admission-tool fix; the frozen init job payload is unchanged.
