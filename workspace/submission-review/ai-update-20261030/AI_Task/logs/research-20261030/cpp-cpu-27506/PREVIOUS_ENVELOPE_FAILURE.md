# CPU prerequisite: bounded process window was too short

Actual job 27387 ended FAILED 124:0 after 93 seconds on g1, zero requested/allocated GPUs and two CPUs. It did not complete the C++ fixture and cannot qualify S106.

The fixed 90-second process window included container creation. Actual Enroot creation took 76 seconds; Torch import took 2.142 seconds. Only 14 seconds remained after container creation for imports, cold C++ JIT and fixtures. The final CPU result has empty fixture cases and state FAIL_TIME_LIMIT_OR_SIGNAL. Eight pre-build source hashes, compiler/Ninja/PyTorch versions and hidden-GPU checks were recorded. No successful C++ binary, post-build source record or fixture result exists. This does not establish an unsupported extension.

The outer timeout terminated srun itself. No native cleanup-end marker is present. Do not call cleanup complete or assume the exact rootfs still exists; inspect its allowlisted path and process ownership only inside an authorised allocated step on the original host. Original logs and failure JSON are sealed and unchanged.

Prepare a new bounded R2 stage with zero GPUs, four CPUs, 16 GiB and six minutes. Use an internal 300-second process deadline so native cleanup can complete before the scheduler limit, preserve the original source/toolchain/fixture and zero-GPU scope, and review residual state explicitly. The longer envelope is justified by actual setup cost and revises an agent-created bound under the owner's existing Slurm authorization. It is not a request for extra PBS spending or a silent extension of 27387.

Observed cost is 0 allocated GPU-hours and 0.051667 CPU-hours; maximum original reservation 0.066667 CPU-hours. The partition's exclusive placement occupied one node during the 93 seconds even though it allocated no GPU resource. No PBS SU. Full model integration, output quality, official accuracy and performance remain unmeasured. Keep S106 blocked until an actual reviewed replacement prerequisite passes.
