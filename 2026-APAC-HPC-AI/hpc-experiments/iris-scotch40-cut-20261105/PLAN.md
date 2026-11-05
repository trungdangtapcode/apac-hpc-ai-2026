# Iris Scotch 40-domain cut plan

The reviewed first 40-step 48-versus-56 native comparison favored 48 ranks by 17.38%; a reverse-order confirmation passed root and independent replay with a 19.21% reduction on the same Iris node, while the first 48-rank repeat pair showed about 15% variation. The next distinct hypothesis is that 40 Scotch domains may further reduce rank density and communication overhead. This cut only creates and validates the partition; it does not measure solver performance.

The sole pinned case change is `nCores: 48 -> 40`; Scotch remains selected. The official serial mesh and all other case inputs remain hash-identical. The job uses one exclusive 56-CPU Iris node, one serial task, zero GPUs, low QoS, a 40-minute cap, and a 30-minute `decomposePar` cap.

Acceptance requires exact processor directories 0 through 39, all six restored initial fields in each, native v2512/scalar64 completion, 40 positive domain cell counts totaling 65,334,765, full eight-file mesh identity, and source hashes before and after. No READY marker or solver stage is included. A later 40-rank solver comparison must follow native initialization and use a matched control.
