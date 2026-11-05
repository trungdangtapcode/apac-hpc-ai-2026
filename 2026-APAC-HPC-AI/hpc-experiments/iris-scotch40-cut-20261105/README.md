# Iris Scotch 40-domain cut qualification

## Question and controlled change

The reviewed first 40-step native rank-density comparison favored 48 ranks over 56 by 17.38% in aggregate mean time. A reverse-order confirmation passed root and independent native replay with a 19.21% reduction on the same Iris node. A separate Scotch48 repeat pair varied by about 15% in the first trial, so this follow-up prepares a 40-domain Scotch cut to test a lower rank density. These are measured signals, not proof that 40 ranks will be faster.

This cut changes only `nCores` from 48 to 40 in the pinned case definition, which controls `numberOfSubdomains`. The official 65,334,765-cell serial mesh, its eight full-file hashes, initial fields, physics dictionaries, and all other source pins are unchanged. The cut artifact is unique: `artifacts/cut-N40-scotch`.

## Stage and resource limits

One exclusive Iris node, 56 CPUs, one serial task, zero GPUs, low QoS, and a 40-minute wall-time cap (37.333 allocated CPU-hours). Native `decomposePar -constant` is capped at 30 minutes. Before decomposition the job hashes all eight mesh files and all pinned source inputs. It restores the six initial fields and requires exactly `processor0` through `processor39`, 40 positive native cell counts summing to 65,334,765, and all six restored fields in every partition. Logs are retained.

This payload is cut-only. It does not mark a case READY, run renumbering, potential initialization, boundary-layer application, or any solver. A later solver comparison needs those native initialization stages and a matched control; no solver performance or score claim follows from this cut.
