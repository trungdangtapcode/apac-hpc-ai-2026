# Scotch48 native cut passes

Iris job **2294914 COMPLETED 0:0** in **264 seconds** on iris001 with 56 allocated CPUs. The exact 48-domain gate passes: **65,334,765 cells**, **288 restored initial field files**, and 48 per-domain cell records. Minimum cells/domain is 1,348,830; maximum is 1,375,003, or 1.010184 times the mean. This is cell balance, not measured communication or solver performance.

All ten transferred artifacts match their SHA-256 and size. Full eight-member official mesh identity, 45 payload hashes before/after, native v2512/scalar64/End and absence of fatal markers pass. The source cut and previous runs are retained. GNU time reports 33,311,932 KiB peak RSS and 98% process CPU; these are serial decomposition resources, not bandwidth or solver telemetry. Hardware counters were not collected.

Actual allocated cost is 4.106667 CPU-hours, conservatively 5. The 37.333333-hour reservation was retired once, leaving 1,225 consumed /zero reserved under the unchanged 1,289 internal stage. Site SU is unknown.

The cut is not READY and no faster solver result is claimed. Next is the mandatory native initialization chain (renumberMesh, potentialFoam, applyBoundaryLayer), with independent source/field/output gates, before a matched 48-versus-56 solver measurement.
