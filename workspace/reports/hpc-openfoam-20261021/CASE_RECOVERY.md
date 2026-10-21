# Exact case recovered and Basic text preparation checked

**Access update:** [Interactive login now reaches the actual Iris cluster](IRIS_ACCESS.md). Earlier gateway-only observations below are historical; they did not establish a submission restriction.

On the next owner status checkpoint, the source-access investigation found the
migrated official committee project at
https://gitlab.com/openfoam/community/hpc (public project 83806040). The old
committees/hpc namespace was the wrong migrated path, not evidence that the
case was unavailable. The original develop.openfoam.com raw/API endpoints
still returned 403; GitLab's community project API succeeds.

The requested short commit 84c26243 resolves to
84c262431117f5c921db8335e368a12d0e9fa3f0. This is the exact commit named in
the organisers' public Gadi/ASPIRE reference notes. Retain 42 text files,
77,481 bytes, under case-recovery-20261021/case, without downloading the mesh
or illustrations. Every file's Git blob hash matches the pinned tree; retain
SHA256, mode and source URL in the manifest. HTML responses are rejected.
The earlier full-case access blocker is therefore resolved; retain its failed
attempts as historical rather than continuing to describe source as missing.

Recovered files include Allrun, all initial fields, transport/turbulence
properties, fvSchemes, fvSolution.fixedIter, controlDict.noWrite, the case
definition, function objects and required probe inputs. The case timer source
is retained unchanged. Copying these files is not a simulation or a measured
performance gain.

## Verified preparation helper

The new tools/prepare_basic_case.py derives only the allowed Basic text
settings. It verifies frozen source hashes, chooses the documented Gadi or
ASPIRE-2A full-rank geometry and 40/80/150 endpoints, changes nCores/method/
applicable hierarchical factors and endTime, and selects the exact fixed-work
fvSolution and noWrite control file. The other inputs remain byte-identical.
It refuses an existing destination and creates no mesh or scheduler job.

A temporary-directory validation prepares 12 combinations: two platforms,
three node counts, two Basic methods. Rank geometry, endpoints, unchanged
inputs and original Allrun shell syntax pass; overwrite is rejected. These
are static preparation checks, not 12 CPU benchmarks or a numerical Cd pass.

```bash
python3 /home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/tools/prepare_basic_case.py \
  --platform gadi --nodes 4 --method scotch --output /path/to/new-case
```

Do not submit the original Allrun directly: its generic SBATCH example requests
partition arm and 512 tasks. Those headers are not Gadi/Iris queue instructions.
A correct site job must load v2512 and run bash Allrun or the complete split
chain. Using bash also avoids its login-shell shebang resetting a loaded module,
as noted in the organisers' Gadi instructions. The full mesh, correct site
resources and observed exit/output gates are still required before execution.

## Actual access and next decision

A fresh login-shell query to the supplied endpoint still returns
instance-20210305-2210, with no scheduler in PATH or the documented Iris kit.
The sanitised recheck timestamp is retained in the linked access record.
Endpoint authentication works. The unresolved item is the real compute
service/next hop or a confirmed alternative team CPU account, not the private
key. Other relay users' account entries are not used.

Next obtain that route, inspect its actual module/project/queue and practice
kit, then run a bounded full-chain Basic baseline. No CPU job, mesh download,
new reservation, AI modification or authentication restart occurs here.

- [Recovered-source manifest](../../../2026-APAC-HPC-AI/hpc-experiments/case-recovery-20261021/manifest.json)
- [Preparation validation](../../../2026-APAC-HPC-AI/hpc-experiments/case-recovery-20261021/preparation-validation.json)
- [Frozen Allrun](../../../2026-APAC-HPC-AI/hpc-experiments/case-recovery-20261021/case/Allrun)
