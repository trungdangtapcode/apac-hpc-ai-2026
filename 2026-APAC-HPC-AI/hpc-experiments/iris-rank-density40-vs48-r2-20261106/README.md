# Iris native Scotch40 versus Scotch48

This package prepares one controlled four-arm ABBA comparison of 40 and 48 MPI ranks on iris001. It holds the official mesh, solver physics, runtime, default MPI policy, uncollated I/O and 40-step horizon fixed. The N40 case is accepted only from the terminal reviewed Scotch40 initialization job 2294998; the N48 case uses the already accepted initialized source.

Read [PLAN.md](PLAN.md) for the hypothesis, design, evidence limits and admission gates. `run.py` records timing, force, source, runtime and available telemetry evidence. Offline checks do not claim that the job is deployed or submitted.
