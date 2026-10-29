# Actual C++ radix CPU preflight accepted

Observed 2026-10-29T22:42:29.439775+07:00, Vietnam time (UTC+7). Slurm accepted **27387** for the frozen source-pinned CPU/JIT fixture. It is a submitted prerequisite, not a runtime pass or a model-performance result.

Resources: one node, zero GPUs, two CPUs, 16 GiB memory, two-minute scheduler limit; process deadline batch-start+90 seconds with up to30 seconds for cleanup. Maximum requested CPU occupancy0.066667 CPU-hours, GPU-hours0 and PBS_SU0. Fresh queue/cap5, manifest, native runner and sbatch checks were reviewed under the Slurm admission lock. Existing27378/27383 positions remain untouched.

This cold private-cache import must build the native host C++20 extension and pass CPU int64 index-map invariants at page1 and metadata-only page16. Runtime source pin is checked before JIT. No Qwen weights or GPU tensor work; no scratch/model mount. Private build caches are removed rather than archived. Binary hash/toolchain/source/timing and original errors are retained where available.

Even a complete pass does not establish production RadixCacheCpp allocator integration, eight-rank P selection, P/D ownership, model output, accuracy or speed. The future full C++ candidate is preparation only and must not be called ready until this actual prerequisite is reviewed. Missing compiler, timeout or failed invariant is a failed diagnostic; preserve it and do not silently extend this frozen trial.

Current observed own queue:

    27387|ap42-cpp-radix-cpu|PENDING|0:00|1|(Resources)
    27383|ap42-s105-tc54|PENDING|0:00|2|(Resources)
    27378|ap42-s104-pcache|RUNNING|11:22|2|g[1,4]

The frozen sources were captured before admission in2a7d74c3; root added an explicit16GiB memory limit and regenerated the pin before sbatch. Actual acceptance/reservation and final hash are saved separately. No previously submitted payload, HPC, published submission, authentication or background automation changes. Git pushes do not upload sibling external object bytes.
