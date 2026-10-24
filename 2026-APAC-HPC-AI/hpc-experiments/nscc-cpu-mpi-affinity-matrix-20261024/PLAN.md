# Test binding interfaces and explicitly preserve the launcher's mask

## Hypothesis and prior observation

Job 25956623 directly captured 512 pre-init singleton masks becoming CPUs0–255 after MPI_Init. All ranks skipped core/NUMA reads because the post-init mask was not singleton. The exact internal cause is unknown. The current strict placement gate correctly blocks solver tests.

The installed PALS 1.1.6 manual documents the environment binding route as well as the already-used explicit thread option. The installed Cray MPICH 8.1.15 manual documents rank reordering but yielded no documented affinity-preservation setting in this review. Test interface behavior rather than assume an undocumented environment knob.

## Bounded matrix

1. Advisory method 0 with the existing explicit thread binding tests association with custom reordering. This is not the target method 3 mapping and cannot qualify it.
2. Advisory method 3 with documented PALS_CPU_BIND=thread instead of the global CLI bind option tests the launcher's binding route. Both advisory controls retain failures and have 25-second per-launch deadlines.
3. Strict method 3 identity uses an opt-in PMPI shim loaded only by the application. It snapshots the calling thread's pre-init mask, calls the original PMPI_Init/PMPI_Init_thread, restores exactly that singleton mask and rereads it. The original C probe then independently checks actual post-init affinity/core/NUMA.
4. If identity fully qualifies, render the original aggressive candidate on the actual identity slots and require the complete candidate world-rank/host/core/NUMA mapping. No balanced substitution or weakened topology gate.

The profiling mechanism is defined by the [MPI Forum profiling requirements](https://www.mpi-forum.org/docs/mpi-1.1/mpi-11-html/node153.html). That source establishes named PMPI entry points, not the safety or performance of this particular affinity intervention. Real library execution and OpenFOAM compatibility remain to be tested. Only the initializing thread is restored; helper threads and page residency are outside this experiment's proof.

The previous collective failure shutdown reached its timeout. This derived diagnostic aborts after all categorized records have been emitted and the failure count is known. Advisory failures remain visible as failures; only successful strict identity and candidate validations can produce the final PASS marker.

## Gates, cost and next decision

Local synthetic PMPI tests pass both entry points, pass-through, invalid masks, restore/read failures and failed init handling. Existing mapping fixtures pass one positive and reject seven negatives. C builds only on the future compute allocation; no actual Cray/PMPI or mapping pass is yet claimed. Source and assignment are pinned. Preload is never applied to the launcher, and an inherited preload is rejected.

Four exclusive CPU nodes × 128 ranks, 32 GB/node, no GPUs, 5-minute wall maximum,255-second internal deadline: **42.666667 SU** maximum. Fresh rate/balance and combined CPU/AI PBS cap checks under the existing CPU lock are mandatory. Current remaining-grant authorization permits this bounded followup. The failed parent stays unchanged. If the shim fails linking, restore proof, or exact world mapping, stop and inspect that specific failure before any further fix. If it passes, prepare a separately sealed solver comparison with identical qualified binding/shim in identity and candidate, fresh allocation mapping and official 150-step numerical work.
