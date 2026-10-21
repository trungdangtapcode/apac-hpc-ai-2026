# Start here

Practice scripts for this cluster. They are examples, not a required
template. Cluster wall-clock is not a score. The contest quantity is
**average wall-clock time per time step**.

Do not `sh` a `.sbatch` file. Do not run jobs from the group
`reference-scripts` tree. What each script does, and why a new split
needs a new directory, is in `LADDER.md`. 65M prep flags follow
[Allrun](https://develop.openfoam.com/committees/hpc/-/blob/develop/incompressible/simpleFoam/occDrivAerStaticMesh/Allrun)
(not Allrun’s 512-rank / 4000-step example). The working copy drops that
`Allrun` file so you do not submit it; the URL is still the source.

## One-time

Make a folder under
`/global/exafs/users/rdmaworkshop30/apac2026/` and `cd` there. That
folder is your work root. It is visible to everyone on this login. Do
not use the `apac2026` directory itself. Do not copy the example name.

```bash
mkdir -p /global/exafs/users/rdmaworkshop30/apac2026/blue-kettle
cd /global/exafs/users/rdmaworkshop30/apac2026/blue-kettle
~/00-sync-kit.sh
cd kit
bash ./01-binaries.sh
sbatch 02-toy-stages.sbatch
```

`00` copies the examples into `./kit` and points `kit/runs` at `../runs`.
Stay in `kit` for `01` and for every `sbatch`. Watch logs with
`tail -f runs/<jobid>.out`. Later jobs:

```bash
sbatch 03-prep-65M-N56.sbatch
```

Scotch and simple cuts at the same three sizes are later numbers
(`13`–`19`, `23`–`29`). See `LADDER.md`. Do not reuse `ready-N56-h742`
for those cuts.

To refresh the examples after the group kit changes, `cd` back to the
folder above `kit` and run `~/00-sync-kit.sh` again.

Exit code 0 means pass. If a job fails, read `./runs/<jobid>.out`.
