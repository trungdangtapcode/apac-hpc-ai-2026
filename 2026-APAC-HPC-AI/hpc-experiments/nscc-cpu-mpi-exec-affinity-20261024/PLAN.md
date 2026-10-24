# Earlier capture provenance for a strict affinity repair

## Question and prior evidence

Can the captured pre-exec launcher CPU survive MPI initialization when later entry-time mask capture proved unreliable? Job 25957267 restored 253/512 ranks and rejected 259 broad entry masks. Its no-shim method 0 and PALS-environment controls also lost binding; do not repeat those unchanged alternatives. Preserve the complete failed matrix and its 3.413333-SU terminal estimate (rounded 4-SU allowance), not just the partial successes.

## Controlled intervention

Use the same module, explicit thread binding, method 3 reorder, original aggressive assignment, topology and mapping acceptance gates. Replace only the affinity target's capture point: capture the actual singleton launcher CPU in a Python exec wrapper before starting the MPI application. Propagate that exact integer and preload the PMPI shim only in the exec'd app. The shim reads contemporaneous masks for diagnostics, restores the captured CPU after the original PMPI initializer and verifies it. Fail on missing/invalid provenance or restoration; no CPU arithmetic heuristic.

Qualify strict identity and candidate using MPI_Init_thread(SINGLE), then plain MPI_Init and MPI_Init_thread(MULTIPLE) identity. The installed OpenFOAM 2512 Pstream source at `/app/apps/openfoam/2512/OpenFOAM-v2512/src/Pstream/mpi/UPstream.C`, lines 178 and 243, uses MPI_Init_thread and requests SINGLE or MULTIPLE according to needsThread. That source observation does not prove the actual loaded binary's call: retain initialization audits in any future solver run. The [MPI Forum profiling requirements](https://www.mpi-forum.org/docs/mpi-1.1/mpi-11-html/node153.html) establish PMPI entry points, not safety or performance of this intervention.

For each arm, join 512 pre-exec capture records to 512 PMPI world-rank audits and 512 independent post-init C topology records. Use captured PMI only for original-process association; actual world-rank and physical mapping are validated independently. All exact topology and candidate checks remain mandatory. This restores only the MPI-calling thread; helper threads and page residency are not proved.

## Verification, budget and next decision

Local mocked PMPI tests cover both entry points, late widened masks with a valid pre-exec CPU, malformed/missing/out-of-range capture, failed syscalls, init errors, pass-through and exec-wrapper rejection. Python3.6 grammar, Bash syntax, existing randomized mapping fixtures and explicit positive/negative record-join fixtures pass. No real Cray build, mapping or solver pass is yet claimed.

Request 4 exclusive CPU nodes × 128 CPUs/ranks, 32 GB/node, 0 GPUs, 5-minute wall,255-second internal deadline; maximum 42.666667 SU. Use the existing locked remaining-grant authorization, fresh site rate/balance and combined CPU/AI cap checks. Only after actual strict identity/candidate/thread-entry qualification may a separately frozen solver comparison be admitted. The conditional ABBA design preserves fixed 150 steps and all 149 timings with matched launch treatment; no numerical-work or output shortcuts.
