# Derived four-node topology diagnostic

The prior job 25947168 failed its combined single-CPU/core/NUMA gate before any candidate launch. Its log cannot identify which subcheck failed. This version preserves that exact aggressive scientific mapping, resource request and strict acceptance gates. It records each rank's affinity before and after MPI_Init, physical-core lookup status and NUMA lookup status, then uses a collective failure decision to preserve all diagnostics. Local synthetic MPI tests do not establish a cluster fix.

If identity and candidate validate, this qualifies only this allocation and mapping. It runs no solver and claims no speedup. The balanced whole-group candidate remains separate and unsubmitted.
