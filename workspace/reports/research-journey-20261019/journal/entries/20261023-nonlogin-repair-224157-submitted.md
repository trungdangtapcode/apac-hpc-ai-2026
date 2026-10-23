# Nonlogin repair 224157 is submitted for real confirmation

At 2026-10-23T15:49:28.547700+00:00, PBS accepts 224157.pbs111 and immediately runs it on H100 hosts 037/039. Two GPUs, ten-minute maximum, at most 42.666667 SU. The prior 18.631-SU charge is uniquely posted; new headroom 4472.788333 SU under unchanged 51000 cap / 13000 reserve. No CPU project budget or HPC task is touched.

The [predeclared supported repair](20261023-nonlogin-repair-preparation.md) removes login Bash at both launch boundaries and initializes the required module explicitly. Everything native, strict errors, source/data geometry and independent success gates stays unchanged. The same host pair names as 224155 reduce one host-pair difference, but GPU assignment and filesystem/timing may differ; confirm actual UUIDs and phase samples rather than assume an exact repeat. Source and CPU proof were pushed as 70f4094b before submission.

No terminal result exists at submission. Require complete native byte/hash proof, all Python/container/node/batch zero exits and final PBS exit 0. A clean pass would confirm this launcher repair and preserve remaining full-model/auxiliary-row uncertainties. A failure requires its actual error layer and a new decision, not a blind retry. [Receipt and allocation bounds](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nixl-nonlogin-exitfix-20261023/RESULTS.md).
