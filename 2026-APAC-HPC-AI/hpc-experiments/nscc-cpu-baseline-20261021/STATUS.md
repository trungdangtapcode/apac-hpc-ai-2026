# CPU baseline preparation receipt

25904959.pbs101 accepted 2026-10-21T14:10:12.031377+00:00 under CPU project
59000042. Fresh official hierarchical N128 payload is hash verified. Separate
CPU lock, fresh project/own queues and combined PBS cap precede qsub. Maximum
32 CPUs/96 GB/one serial process/zero GPU/900 seconds, 8 SU. The parent CPU
ledger retains prior probe maxima and this maximum, total 10.666667 SU.

The job also checks native semantic expansion of the Iris control before mesh
work. Terminal history is already F/exit1 after16s; inspect the actual diff
before any retry. No prepared CPU split, solver result or score is claimed.

## Terminal review and exact cause

The native dictionary expansions differ only in one generated header comment:
// "system/controlDict" versus // "actual-controlDict". Replacing only that
single known filename comment makes the complete expanded bytes identical;
all numeric entries and coded-function bodies match. Thus this is a validator
metadata false rejection, not a changed CFD input. The Iris control semantic
check is now supported by retained native expanded dictionaries.

25904959 F/exit1 after16s stops before mesh hashing/decomposition, so no CPU
prep pass is claimed. Estimated base charge0.142222SU, posted charge not yet
reconciled; keep max8SU conservatively reserved. Derive a new payload which
normalizes exactly this one generated header, rejects every other difference,
and keeps case, resource envelope and mesh checks fixed. To stay under100SU
with every conservative maximum, the later conditional128CPU init+solve will
be limited to35min (74.666667SU), not the earlier40min planning example.
