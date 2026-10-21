# Iris access resolved: interactive gateway login is required

The owner's organiser email explains the missing step: the Iris gateway performs
an automatic cluster jump for an interactive login. Earlier SSH commands supplied
a remote command, so they executed on the gateway VM and bypassed this jump.
Adding bash -l inside that remote command did not reproduce an interactive SSH
login. The missing scheduler there was a property of the gateway endpoint, not
proof of an Iris account restriction or an outage. Preserve those observations
as historical; their interpretation is corrected here.

The actual successful sequence was an SSH login with a forced terminal and no
remote command, then waiting for the inner prompt before issuing commands:

```bash
bash /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/tools/iris-interactive.sh
# After the prompt becomes rdmaworkshop30@login01:
hostname
sinfo -p iris
squeue -u "$USER"
```

The helper references the existing private key; it does not copy, print, embed
or upload it. Do not use scp or a one-command SSH call to the gateway and assume
its local filesystem is Iris storage. Confirm the cluster hostname and path.
An initial stale control-socket warning was followed by successful cluster login;
no socket pool or other user's authentication state was modified.

At the fresh 2026-10-21T11:21:05Z read, the session returns:

- Host: login01.hpcadvisorycouncil.com.
- User/home: rdmaworkshop30, /global/home/users/rdmaworkshop30.
- sbatch, srun and sinfo: /usr/bin executables.
- Iris partition: up, 32 nodes, 56 CPUs and 180000 MB advertised per node.
- Account queue: empty at that read. A later allocation-state read shows 31 idle
  and one reserved node; these are dated snapshots, not promises of availability.
- The exact documented group OpenFOAM reference-scripts directory is present.

The kit README/LADDER were read. Create a uniquely named work root under
/global/exafs/users/rdmaworkshop30/apac2026; never submit from the shared group
kit or the common apac2026 root. The account/key are shared, so avoid touching
other work roots or cancelling unrelated jobs. Our work root is
/global/exafs/users/rdmaworkshop30/apac2026/tripleu-hpc-20261021T1121.
The kit was synced only into this new work root. The supplied 01-binaries.sh
passes on the login node, showing the native v2512 build prefix 87ed40d256.
Its source and preflight output are retained with hashes under
hpc-experiments/iris-practice-20261021.

Do not execute the Iris-optimized simpleFoam/foamHasLibrary ELFs even with -help
on the login CPU; the kit documents SIGILL there. Run actual solver execution
only inside the Slurm allocation. The current kit uses gcc/11 and hpcx/2.50;
do not substitute the older ISC example's compiler or v2412 recipe.

## Next bounded practice gate

The first distinct test is the supplied 02-toy-stages.sbatch, unchanged:
one Iris node, four MPI ranks, at most five minutes. Iris allocates whole nodes,
so four ranks does not mean a four-core-only allocation. The maximum occupied
capacity is one 56-CPU node for five minutes. This is a toy motorBike deployment
and decomposition check, not the 65M scored case. It checks both hierarchical
and scotch in separate run directories. It intentionally has a toy-specific
preparation chain; it cannot replace the required 65M chain or its Cd proof.

The immediate question is whether the native compiler/MPI/solver stack works on
allocated compute CPUs. Passing binary inspection on login does not establish
that. Preserve actual job receipt, scheduler exit, stage logs, split identity
and solver End markers. No throughput improvement or contest result follows.
Only after this gate should a bounded 65M practice preparation be considered.
No NSCC/Gadi project, AI allocation or GPU job is involved in this practice gate.

## Observed terminal result

Job 2293751 is now COMPLETED/exit 0:0 in 30 seconds on iris031. Actual allocation is 56 CPUs, one node, with four MPI ranks. Both ten-step toy methods and sealed stage/split/hash checks pass. The timer warns of insufficient samples for its confidence target; no useful speedup, 65M Cd proof or official score is claimed. See the retained review under hpc-experiments/iris-practice-20261021.
