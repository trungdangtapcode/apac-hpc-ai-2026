# Fresh official CPU baseline: serial preparation

The native CPU timing gate 25904765 passes. Recovered October 10 processor
trees are not accepted as valid current inputs. Prepare a fresh official
hierarchical N128 case (16 4 2), one-node/40-step convention, pinned source
84c262431117f5c921db8335e368a12d0e9fa3f0. This job does not run simpleFoam.

Allocate 32 CPUs/96 GB, one serial process, zero GPUs, maximum 15 minutes:
maximum 8 SU at the verified 1 SU/core-hour rate. The larger CPU allocation
provides a conservative memory envelope, not parallel decomposePar. Keep
one own CPU allocation; existing probe maxima 2.666667 + prep8 + conditional
128CPU/40min solve85.333333 = 96 SU, below the first 100-SU wave ceiling.
Only preparation is reserved now; parallel init+solve requires reviewed prep.

First use the allocated native v2512 dictionary parser to independently check
the Iris controlDict's semantic expansion after its two intended edits. The
Iris script expands includes when setting startFrom/endTime; byte comparisons
alone are invalid. Stop before mesh work on any semantic mismatch. This is
artifact validity checking, not a changed solver or numerical workaround.

Verify the official shared archive's published MD5 and SHA256, then stream all
archive members and compare them with the existing unpacked mesh's size and
SHA256. This avoids another mesh download and actually verifies full content;
all I/O and preprocessing occur in the allocation. Do not rewrite old data.
Then use our fresh pinned case, decomposePar -constant and restore0Dir.
Require clean native exits/End, 128 processor directories and 65,334,765 total
cells plus every initial field. Preserve failed output. CUT_READY is not the
full parallel initialization READY and cannot authorize skipping any stage.

The code keeps official fixedIter, schemes, physics and function objects.
Subsequent full initialization+40-step solve uses a separate reviewed payload
and reservation. No GPU/AI work or ledger changes. CPU project59000042 uses
the existing dedicated lock/ledger from nscc-cpu-timing-probe-20261021.
