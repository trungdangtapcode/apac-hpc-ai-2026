# Read-only compiler-rule review

The retained Iris rule `wmake/rules/linux64Gcc/c++Opt` contains `-O3` and an unconditional `-march=cascadelake`; prefs select Gcc, SYSTEMOPENMPI,DP,Int32 and Opt. Exact source text and SHA-256 are pinned in `rules.json`. This is an inspection of the currently installed rule tree, not proof of every flag used to build the existing binary. No compile commands or complete binary build log were collected.

Do not assume the reference is generic/unoptimized and launch a blind `-march=native` rebuild. Any architecture-build hypothesis must first preserve actual binary/source provenance and choose a distinct verified change. This read-only inspection runs no compiler, solver or job, and changes no environment or configuration.
