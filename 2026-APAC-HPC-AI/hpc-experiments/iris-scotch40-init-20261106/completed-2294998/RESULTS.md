# Scotch40 initialization terminal review

**Iris 2294998 COMPLETED 0:0** in 128 seconds with 56 allocated CPUs on iris001. The exact N40 Scotch artifact is initialized and has the pinned READY marker. This is preparation, not a solver benchmark.

The native cut/accounting gate verifies job 2294919, the complete eight-member official mesh identity and 65,334,765 cells, 40 processor domains and 240 restored fields. The initialization preserves the organizer sequence and arguments: renumberMesh -constant -overwrite -parallel, potentialFoam -initialiseUBCs -parallel, then applyBoundaryLayer -ybl 0.0450244 -parallel. All three logs have return code zero, native End, OpenFOAM 2512, scalar64, 40 ranks and no fatal markers.

The forty separate rank JSON proofs pass the exact qualified strict reader: every expected rank once, world size 40, one host, nonempty disjoint CPU masks. Both source pin checks pass with identical 41-file input hashes; payload hashes pass before and after. The two field inventories each contain all 240 exact rank/field paths. Field value hashes change across required initialization, as expected. READY is written last with the exact N40 Scotch/65M marker.

The full initialized case inventory contains 752 regular files, one approved shared constant/polyMesh symlink and 13 supplementary files across 166 directories. The 68 transferred evidence files and their 23,050-byte compressed archive all verify. GNU time records the three per-stage peak RSS values; Slurm batch-step MaxRSS is 79,937,828 KiB, while the root-job field is blank. These quantities do not establish aggregate resident memory or bandwidth.

Actual scheduler allocation cost is 1.991111 CPU-hours; billed SU is unknown. No solver timing or performance gain is claimed. Next, use the frozen accepted-source manifest for a separately reviewed matched 40-versus-48 solver comparison.

Evidence: collection.json, raw-evidence.tar.gz, collected/, accepted-source-manifest.json, supplementary-source-manifest.json, and REVIEW.json.
