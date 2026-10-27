# 27 October: submit the real OpenFOAM integration qualification

**Prior evidence and hypothesis.** Native post-initialization pinning qualifies all 512 main threads. This next test asks whether the same mechanism survives the actual Pstream entry and shutdown paths rather than only a standalone probe. The installed source and dynamic symbols were inspected before choosing the hooks.

**Actual admission.** Job **26019383.pbs101**, submitted once at **2026-10-27T05:24:00.607094+00:00**, has three arms: unchanged native control, adapter-backed native control, and real checkMesh on a tiny 8,192-cell diagnostic mesh. It holds four CPU nodes, 512 ranks and method-0 settings fixed. The official contest case and solver are untouched. Fresh own CPU and AI PBS queues were empty under the established locks. At 05:25:41 UTC, PBS reports Q/q5 waiting for node_pool. [Frozen source and receipt](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-cpu-pstream-latepin-20261027/STATUS.md).

**Acceptance and limits.** Require all initialization/topology/main-thread audits, native MPI summaries, physical-core uniqueness, application version/precision/rank/cell counts, complete Mesh OK/End output, pre-finalization masks, and actual PMPI_Finalize return codes. Preserve source and runtime hashes, every command status and phase resource report. Offline checks pass but are not real adapter ABI/runtime evidence. No solver-speed, helper-thread, NIC or official-result claim follows from this admission.

**Cost.** Maximum 600 seconds on 512 allocated CPUs reserves 85.333333 SU at verified rate one. Conservative commitment is 4,857.2 SU and headroom 24,920.646667 SU under the existing 29,777.846 ceiling. Unknown older maxima remain unchanged. No additional spending envelope or background schedule was created.

**Next decision.** Independently replay every completed arm before preparing a full DrivAer native-versus-pin comparison. A later ABBA test must use isolated fully initialized copies, unchanged 150-step numerical work, actual matching mappings and complete force/timing checks. Its clone cost cannot be inferred from the old tiny input-case copy. Failed integration closes this exact adapter version and requires a log-derived correction, not a score claim or blind repeat.

**Preservation.** The actual receipt and reservation are a separate small checkpoint after the reviewed hypothesis. Existing submitted payloads, AI work and submission materials remain unchanged.
