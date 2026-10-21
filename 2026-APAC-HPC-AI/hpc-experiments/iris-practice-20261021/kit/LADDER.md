# Script ladder

How to submit is in `README.md`. This file is the rest: what the
examples are, and what breaks if you reuse a split.

## These are examples, not requirements

- **These scripts are not required.** You do not have to submit practice
  logs, use 4 ranks on the toy case, or follow this exact decomposition.
- **Cluster wall-clock is not a score.** Times from these scripts are practice readings only. The contest quantity is **average wall-clock time per time step** (the simpleFoam log line from the case; from the second step on).
- **These rank counts and decompositions are not required.** They are
  working data points on this machine. On this v2512 build you can try
  `hierarchical`, `simple`, or `scotch` (`01` checks `libscotchDecomp.so`).
  `kahip` is named in the 65M dict but is not compiled here. A new split
  belongs in a new directory (toy: each `sbatch` uses a new job-id folder;
  65M: a new `ready-*` name). Do not overwrite `ready-N56-h742` with a
  different split.

Do not use ExecutionTime or cells/second in place of that average.

## Official Allrun

The command sequence and dictionary copies for the 65M case come from
[Allrun](https://develop.openfoam.com/committees/hpc/-/blob/develop/incompressible/simpleFoam/occDrivAerStaticMesh/Allrun)
on `develop`. Copy `fvSolution.fixedIter` and `controlDict.noWrite` **before**
`decomposePar`, then:
`decomposePar -constant`, `restore0Dir -processor`,
`renumberMesh -constant -overwrite -parallel`,
`potentialFoam -initialiseUBCs -parallel`,
`applyBoundaryLayer -ybl 0.0450244 -parallel`,
`simpleFoam -parallel`. These example scripts inline those flags. The
working copy `rm`s `Allrun` so you do not submit Allrun’s 512-rank /
4000-step example; that file is still the source.

What Allrun is **not**: `#SBATCH --ntasks=512`, `ntasks-per-node=128`,
`partition=arm`, and `endTime 4000` inside `noWrite`. This kit uses Iris
rank counts and contest step counts (40 / 80 / 150). `noWrite` ships
`startFrom latestTime`; the `04` / `07` / `09` (and scotch / simple)
solver jobs set `startFrom startTime` so those step counts start from
time 0, not a leftover later time. `05` skips potentialFoam and
applyBoundaryLayer on purpose so you can see the solver still finish;
that skip is not Allrun and is not allowed on a scored run.

## Changing the rank count invalidates the split

The download is a serial mesh (`occDrivAer/polyMesh`). `#SBATCH -n` is
**not** a runtime switch on that mesh. After `decomposePar` the rank count
is baked into the `processor0` … `processorN-1` directory layout. If you
change `-n`, or change `nHierarchical`, the old `ready-N*` artifacts are
invalid — you must re-run the matching prep job.

**Wrong split or skipped initialisation often still finishes and prints
`ClockTime =`.** That is not validation. The solver does not refuse to run on
a stale or mismatched decomposition. Cd values will drift, sometimes
outside the four-pack box, sometimes not. Exit code 0 from the solver
means the solver ran; it does not mean the prep was correct.

Do not interpret `N56` artifacts as interchangeable with `N112` or `N224`
runs. Each `ready-N*` directory is for its own rank count only. The suffix
after `h` is not a git hash: `h742` means `nHierarchical (7 4 2)` because
7×4×2 = 56 ranks (`h744` = `(7 4 4)` = 112, `h784` = `(7 8 4)` = 224).

## One split, one directory

You will try more than these three kit names. That is expected. The mess
starts when two splits share one folder, or when the folder name no longer
matches what is inside.

- **One split = one directory.** Change rank count, `nHierarchical`, or
  `method` (hierarchical / simple / scotch) → new directory. Do not
  `decomposePar` into a folder that already has another split's
  `processor*`.
- **Name the folder after the split**, not after the Slurm job id. Job ids
  are unique, but `runs/624700` does not tell you scotch vs hierarchical.
  Kit example: `ready-N56-h742` means 56 ranks and hierarchical `(7 4 2)`
  only. A scotch 56-rank prep needs a different name (for example
  `ready-N56-scotch`). Reusing `ready-N56-h742` overwrites the kit split.
- **`$WORK/runs/<jobid>/` grows.** Each `sbatch` of `02` copies the toy
  again. Delete old job directories when you are done reading them. The
  kit does not keep a catalog of your variants.

The `processor*` layout still looks the same (`processor0` …). OpenFOAM
will still print `End` and `ClockTime =` if you point the solver at the wrong
tree. The directory name is the label; the solver is not.

## What you can reuse

The group solvers and the uncut `polyMesh` stay as they are. Jobs do not
edit them. Each cut (rank count and cutting method) lives in your own
folder. If that cut has not changed, run `simpleFoam` there again; you
do not have to run `03` every time. Cutting the 65M mesh is slow and
uses disk. That time is not a score.

| What | Keep using it? |
|------|----------------|
| The group solvers, and the uncut `polyMesh` | Yes, always. If you change the rank count or the cutting method, run `decomposePar` again on that same mesh. Do not copy or download the 65M mesh again. |
| The cut folders (`processor0`, `processor1`, …) and `ready-N*` | Only for this rank count and this cut. If you change the rank count, the method, or the numbers in `nHierarchical`, make a new folder. Do not write a new cut into the old folder. |
| `simpleFoam` after `03` has already cut (`04`) | Yes. Run `04` again as often as you want. Do not run `decomposePar` in `04`. The cut folder stays as `03` left it. Step count and the solver log go under `runs/<jobid>`. |
| How many `simpleFoam` steps | This solve job, not the cut. The examples use 40, 80, and 150. You can use another count on the same `ready-*`. |

## What each script touches

| Script | You are touching | Notes |
|--------|-----------------|-------|
| `00-sync-kit.sh` | Your folder under `apac2026/`; rsyncs the group examples into `./kit` | Login node. Home pointer `~/00-sync-kit.sh` |
| `01-binaries.sh` | Group v2512 bashrc; dump `foamEtcFile` and `wmake -build-info`; solvers exist | Login node; do not sbatch. `simpleFoam`/`foamHasLibrary` SIGILL here |
| `02-toy-stages.sbatch` | Same ELFs, then the five toy stages twice at 4 ranks: hierarchical, then scotch | No Allrun. Two folders. Toy times are not a contest |
| `03-prep-65M-N56.sbatch` | 65M decompose→restore0Dir→renumberMesh→potentialFoam→applyBoundaryLayer; writes `ready-N56-h742/` | No `simpleFoam`. One job. Same folder as `03.1` then `03.2`. |
| `03.1-cut-65M-N56.sbatch` | `decomposePar` + `restore0Dir` only. One process; ask for 1 task. `nCores` is still 56 | No `READY`. Then `03.2`. Asking for 56 tasks does not speed this up. |
| `03.2-init-65M-N56.sbatch` | `renumberMesh` / potentialFoam / applyBoundaryLayer on that cut. `-parallel`; ranks must equal the folders | Writes `READY`. One process cannot run this. |
| `04-simpleFoam-65M-N56.sbatch` | `simpleFoam` only, 40 steps, reads from `READY` artifact | No `decomposePar` |
| `05-wrong-skip-init-N56.sbatch` | Intentionally skips `potentialFoam` and `applyBoundaryLayer`; same 56-rank scale | Shows that solver still finishes |
| `06-prep-65M-N112.sbatch` | 65M prep at 112 ranks; writes `ready-N112-h744/` | No `simpleFoam`. One job. Same folder as `06.1` then `06.2`. |
| `06.1-cut-65M-N112.sbatch` | `decomposePar` + `restore0Dir` only. One process; ask for 1 task. `nCores` is still 112 | No `READY`. Then `06.2`. Asking for 112 tasks does not speed this up. |
| `06.2-init-65M-N112.sbatch` | `renumberMesh` / potentialFoam / applyBoundaryLayer on that cut. `-parallel`; ranks must equal the folders | Writes `READY`. One process cannot run this. |
| `07-simpleFoam-65M-N112.sbatch` | `simpleFoam` only, 80 steps, reads `READY` | No `decomposePar` |
| `08-prep-65M-N224.sbatch` | 65M prep at 224 ranks; writes `ready-N224-h784/` | No `simpleFoam`. One job. Same folder as `08.1` then `08.2`. |
| `08.1-cut-65M-N224.sbatch` | `decomposePar` + `restore0Dir` only. One process; ask for 1 task. `nCores` is still 224 | No `READY`. Then `08.2`. Asking for 224 tasks does not speed this up. |
| `08.2-init-65M-N224.sbatch` | `renumberMesh` / potentialFoam / applyBoundaryLayer on that cut. `-parallel`; ranks must equal the folders | Writes `READY`. One process cannot run this. |
| `09-simpleFoam-65M-N224.sbatch` | `simpleFoam` only, 150 steps, reads `READY` | No `decomposePar` |
| `10-allrun-onejob-65M-N56.sbatch` | Prep + foam welded in one job at 56 ranks, 40 steps; prints Cd | Costs prep every time; for iteration use `03` then repeated `04` |

## Scotch staircase (same three sizes)

Same cut / init / foam split as `03.1` / `03.2` / `04`. New directories.
`02` already cut a toy graph; these jobs are the 65M version. Times are
practice. There is no welded `13` / `16` / `18` (use `03` / `06` / `08`
if you want one job for hierarchical).

| Script | You are touching | Notes |
|--------|-----------------|-------|
| `13.1-cut-65M-N56-scotch.sbatch` | Graph cut, 56 folders, `ready-N56-scotch/` | One process. Then `13.2`. |
| `13.2-init-65M-N56-scotch.sbatch` | Init on that cut | Writes READY `method=scotch` |
| `14-simpleFoam-65M-N56-scotch.sbatch` | `simpleFoam` 40 steps from that READY | No `decomposePar` |
| `16.1-cut-65M-N112-scotch.sbatch` | Graph cut, 112 folders | Then `16.2` |
| `16.2-init-65M-N112-scotch.sbatch` | Init on that cut | Writes READY |
| `17-simpleFoam-65M-N112-scotch.sbatch` | `simpleFoam` 80 steps | No `decomposePar` |
| `18.1-cut-65M-N224-scotch.sbatch` | Graph cut, 224 folders | Then `18.2` |
| `18.2-init-65M-N224-scotch.sbatch` | Init on that cut | Writes READY |
| `19-simpleFoam-65M-N224-scotch.sbatch` | `simpleFoam` 150 steps | No `decomposePar` |

Do not point `04` at `ready-N56-scotch`. Do not write a scotch cut into
`ready-N56-h742`. `nHierarchical` stays in the dict so `$nHierarchical`
still expands; it is not the scotch cut.

## Simple staircase (same three sizes)

Geometric boxes, like hierarchical, different method keyword. Group
`decomposeParDict` has no `simpleCoeffs`; these cut jobs add it on the
working copy only. New directories.

| Script | You are touching | Notes |
|--------|-----------------|-------|
| `23.1-cut-65M-N56-simple.sbatch` | Box cut, 56 folders, `ready-N56-simple/` | One process. Then `23.2`. |
| `23.2-init-65M-N56-simple.sbatch` | Init on that cut | Writes READY `method=simple` |
| `24-simpleFoam-65M-N56-simple.sbatch` | `simpleFoam` 40 steps from that READY | No `decomposePar` |
| `26.1-cut-65M-N112-simple.sbatch` | Box cut, 112 folders | Then `26.2` |
| `26.2-init-65M-N112-simple.sbatch` | Init on that cut | Writes READY |
| `27-simpleFoam-65M-N112-simple.sbatch` | `simpleFoam` 80 steps | No `decomposePar` |
| `28.1-cut-65M-N224-simple.sbatch` | Box cut, 224 folders | Then `28.2` |
| `28.2-init-65M-N224-simple.sbatch` | Init on that cut | Writes READY |
| `29-simpleFoam-65M-N224-simple.sbatch` | `simpleFoam` 150 steps | No `decomposePar` |

`kahip` is named in the 65M dict but is not compiled here. Do not copy
these scripts and change the method to `kahip`.

Only `10` prints instantaneous Cd against the OHC-1 four-pack at 40 steps ([0.433, 0.436]). Outside the box is a sniff, not a fail. NaN, a missing solver log, or a missing Average line does fail. `04` / `07` / `09` need `End` and `Average wall-clock time per time step`. Contest early-step table also lists 80: [0.334, 0.345] and 150: [0.284, 0.292]; those scripts do not print it.

Group OpenFOAM v2512 is under `…/builds/iris-gcc11-hpcx250-opt/`
(`module load gcc/11` and `hpcx/2.50`, then `OpenFOAM-v2512/etc/bashrc`).
Scripts inline those four lines. `occDrivAer/polyMesh` is already a
**symlink** on the group disk; do not copy or re-download.
`toy-motorBike` is already on the group disk.

Each `.sbatch` file is self-contained: open one file and you see the
whole job.

## Pass/fail convention

Every script's exit code is the verdict (0 = pass). None of them wrap
verification logic in shell tricks that could hide a failure. If a script
fails, check the job's `.out`/`.err` log for the step that failed.

## Suggested order

1. `~/00-sync-kit.sh` — own folder, copy examples into `./kit`.
2. `cd kit` then `bash ./01-binaries.sh` — confirm binaries on the login node.
3. `sbatch 02-toy-stages.sbatch` — see a passing toy log before 65M.
4. `03` then `04` — prep once, run solver. Reuse `04` to iterate. `03.1` then `03.2` is the same prep: one process to cut, then 56 ranks to init.
5. `05` — after a passing `04`, see that skipping init still finishes.
6. `06`–`09` — same split pattern at 2 and 4 nodes. `06.1` then `06.2` (or `08.1` then `08.2`) is the same prep as `06` (or `08`): one process to cut, then 112 (or 224) ranks to init.
7. `10` — all-in-one example with Cd; note the prep cost.
8. After a passing `04`, optional scotch at the same size: `13.1` then `13.2` then `14`. Same pattern at 112/224: `16.1`/`16.2`/`17` and `18.1`/`18.2`/`19`.
9. Optional simple (boxes, other keyword): `23.1` then `23.2` then `24`, then `26`/`27` and `28`/`29`.

Skipping `02` and going straight to a 65M decompose burns allocation before
you have seen what a passing log looks like.
