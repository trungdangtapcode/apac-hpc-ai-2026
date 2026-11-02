# Would moving the HPC experiment to Gadi improve performance?

The owner asked whether submitting on Gadi could produce a better result. **Lower seconds per step than our NSCC 3.364622070 result is plausible; beating the teammate's Gadi 2.079045460 result is unproven.** Moving platforms does not establish that our optimization worked.

## Evidence and inference

The organizer's published Gadi results already show four-node Scotch around **2.126 s/step**, and a prepared-case repeat around **2.088 s/step**. These are measured references, not a forecast or a new measurement of our configuration. Around 2.1 s/step is a reasonable *baseline validation target* for a correctly ported Scotch recipe, not a guaranteed result. [Official Gadi notes](https://github.com/hpcac/2026-APAC-HPC-AI/blob/main/4.2%20OpenFOAM%20Application%20Notes%20-%20Gadi.md).

There is weaker evidence for our hierarchical zyx candidate winning on Gadi. The published default hierarchy reference is about **2.380 s/step**, versus Scotch **2.126** on four Gadi nodes. That is a different hierarchy setting and separate runs, so it does not prove our zyx choice loses; it does warn against assuming an Iris advantage transfers. [Same official reference table](https://github.com/hpcac/2026-APAC-HPC-AI/blob/main/4.2%20OpenFOAM%20Application%20Notes%20-%20Gadi.md).

Iris uses 56 ranks on one node in our experiments; the Gadi scored setup uses 416 across four nodes. A hierarchy port must change the factors, for example from `(7 4 2)` to `(13 8 4)` while testing the same axis-order hypothesis. Node count, partition size, MPI/build and communication regime also change. A relative Iris win is evidence for testing, not a conversion factor for Gadi seconds.

The rules explicitly avoid directly comparing the absolute Gadi and ASPIRE-2A performance numbers. A platform switch alone does not guarantee a higher competition score. [Official task rules](https://github.com/hpcac/2026-APAC-HPC-AI/blob/main/2.%20OpenFOAM%20HPC%20Task%20Rules.md).

## Decision

Keep the accepted Iris measurements and review their complete controls. A Gadi test should establish the site's own baseline and candidate with the same build, resources, workload and full required preparation, then repeat/reverse before attributing a gain. Favor the source-supported Scotch baseline first; do not assume our hierarchy is the best Gadi choice. A controlled four-node 150-step validation is ultimately needed for that platform's scored workload.

No Gadi login/project access or fresh Gadi budget has been supplied to this worker. This answer is an evidence-based outlook; **no Gadi job, cost reservation or result was created**. Existing Iris jobs remain authorized and unchanged. The supplied teammate package's source/timer provenance limits also remain in force.
