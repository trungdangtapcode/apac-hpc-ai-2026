# Native CPU timing-function gate before the 65M baseline

Access is now authenticated on ASPIRE-2A CPU, project 59000042. Its dated ledger
shows 29777.846 SU balance, zero In Doubt and 1 SU/CPU-hour. The queue is empty.
Historical account run 25740797 has zero solver steps and a log stopping at
native coded timing-function compilation; its termination cause is unproven.
Earlier templates also contain unsupported non-Basic numerical controls.

Test the actual site v2512/DP runtime and unchanged official timing function
on its native PitzDaily tutorial, four MPI ranks/five solver steps. This is a
compilation/runtime smoke gate, not the contest case or timing score. Hold the
site module/compiler fixed and change only the diagnostic case size; do not
patch the official timing source or reuse unverified old prepared fields.
All compute and dynamic compilation happen in PBS, not on login CPUs.

First allocation: eight CPUs, four MPI, 24 GB, zero GPUs, maximum 10 minutes;
maximum base rate charge 1.333333 SU. Dynamic compilation is limited to four
build threads and the MPI solver to 300 seconds; preserve resource/time output
and phase markers. Require clean command return codes, native version/DP,
all five contiguous steps, End and Average plus semantic-result.json. Stop this
branch on failure, review actual compiler/runtime output and only retry after
a supported distinct repair. Do not suppress errors because a log contains End.

For this first CPU baseline wave use a planning ceiling of 100 SU and at most
one active CPU allocation. Only this 1.333333-SU probe is initially reserved.
A later serial 16-CPU/20-minute preparation (5.333333 SU) and one 128-CPU/
40-minute full initialization+40-step solve (85.333333 SU) fit below that
ceiling but are conditional and are not yet submitted/reserved. Any resource
normalization, queue limit or shared spending change requires rechecking the
actual maximum before qsub. The displayed ledger is not instantaneous.

Use a separate CPU budget lock and ledger for project 59000042. Never deduct
from or change the AI project's 59010042 budget, serving jobs or payloads.
Check CPU projects/own queues under the lock before the one definite qsub;
retain uncertain outcomes and never blindly repeat them. Existing AI PBS
jobs count toward the combined three-job operating cap; read-only state checks
are allowed. Native timing function provenance is pinned case 84c262431117f5c921db8335e368a12d0e9fa3f0.
