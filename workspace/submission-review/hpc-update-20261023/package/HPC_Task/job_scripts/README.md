# OpenFOAM CPU PBS bundle

This self-contained directory contains a portable PBS job family for the verified OpenFOAM v2512 double-precision CPU environment. Submit from this directory so PBS sets `PBS_O_WORKDIR` to the bundle location. The scripts use `PBS_O_WORKDIR` to locate embedded inputs and write fresh output under `runs/<numeric-job-id>/`; they do not depend on the submitter's home directory on compute nodes.

## Jobs

```sh
cd /path/to/HPC_Task/job_scripts
qsub submit-best.pbs
qsub scaling-1node.pbs
qsub scaling-2node.pbs
```

The project directive defaults to `59000042`; use the site's supported `qsub -P <project>` override if the authorized project differs. The primary job requests four exclusive standard AMD EPYC 7713 nodes, 128 MPI ranks per node, 440 GB per node, no GPUs, normal queue, scatter placement, and 40 minutes. It uses default Scotch decomposition and runs 150 steps. The one and two node scripts are lower-cost unsubmitted scaling checks at 40 and 80 steps. Each has the same per-node resources and 40-minute wall limit. They are not claims of prior measurements.

The driver loads `openfoam/2512`, requires DP precision, uses one OpenMP/MKL/OpenBLAS thread per MPI rank, sets only `FI_OFI_RXM_USE_SRX=0` among `FI_*` settings, and records the effective FI environment. Other FI variables remain at module/site defaults. `WM_NCOMPPROCS` is set to the allocated node count. The shell avoids `nounset` while sourcing site module setup and OpenFOAM `RunFunctions`, which may read optional unset variables; variables consumed by this bundle are checked explicitly. Each execution stage is explicitly timed, bounded, checked for a zero return code, and logged. OpenFOAM command logs must also contain the native `End` marker; the startup rank probe is validated against the requested rank, host, logical CPU, and physical core counts. A wall-clock deadline at 37 minutes leaves cleanup time before PBS's 40-minute limit.

The full initialization chain is serial `decomposePar -constant` (default Scotch), `restore0Dir -processor`, parallel `renumberMesh -constant -overwrite`, `potentialFoam -initialiseUBCs`, `applyBoundaryLayer -ybl 0.0450244`, then parallel `simpleFoam`. Zero-time fields are sealed after restoration and initialization and compared again after the solve. Solver validation checks rank/host counts, all requested time indices, fixed U=15, p=12, omega=8, k=8 iteration counts, native solver and full wall-clock function timers, and finite force-coefficient rows. It deliberately imposes no numeric Cd pass band.

The embedded ASCII case is copied from the accepted `nscc-cpu-scotch128-20261021` case. Its original bytes are hashed and verified before execution. A fresh per-job copy may change only `system/include/caseDefinition:nCores` (128 to the requested total ranks) and `system/controlDict:endTime` (40 to the requested steps). Default Scotch and all other case bytes are preserved. The embedded copy is not a claim that it produced earlier jobs or the 3.677906731 second/step four-node observation.

## Shared mesh setup

The mesh binary is intentionally not included. The default `HPC_MESH_DIR` is `/scratch/users/industry/ai-hpc/apacsc42/apac2026/hpc/shared/polyMesh`; it can be overridden in the submission environment, for example:

```sh
qsub -v HPC_MESH_DIR=/shared/path/polyMesh submit-best.pbs
```

Before submission, arrange read access from compute nodes to the official extracted `polyMesh` directory. The driver checks the eight recorded member names, byte sizes, and SHA-256 values against `mesh-manifest.json` on every run. The official [Zenodo record 15012221](https://zenodo.org/records/15012221) provides `polyMesh_65M.tar.gz`; its pinned MD5 is `50393a15d84f53255fda85ac702390e9`, and the retained archive SHA-256 is `ef30fa8405dbaab77185ace2521b1bedc5650f245e40d7451259a5ac773a5376`. These hashes identify the previously inspected official archive and its unpacked members; the job does not download or unpack it.

## Outputs and evidence limits

PBS combines output into the scheduler's job output file because `-j oe` is set. Detailed stage logs, `/usr/bin/time -v` resource logs, the exact nodefile, rank-to-host and physical-core startup proof, mesh/source checks, phase markers, return codes, field seals, and native solver review are written below `runs/<job-id>/`. PBS log placement and filenames follow site policy.

`batch-lifecycle.json` contains wrapper timing and a best-effort live PBS snapshot taken before process exit. It is diagnostic only; it is not final PBS completion/accounting. Review the terminal scheduler record separately before claiming completion or cost. Startup rank binding does not establish solver-time migration, page residency, or runtime communication. Native timing validation does not establish a confidence interval or causal explanation. The one/two-node examples are scaling checks only; no portability claim, CPU/GPU replay claim, or new measured result is made by this bundle.

`bundle-sha256.json` seals the source files other than itself and generated `runs/` output. `source-case-sha256.json` separately records the 43-file accepted ASCII case. The scripts use Python standard-library syntax compatible with Python 3.6.
