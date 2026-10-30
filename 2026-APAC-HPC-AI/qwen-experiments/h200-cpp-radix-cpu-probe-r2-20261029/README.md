# C++ radix-tree CPU preflight, retry proposal R2

**State: prepared for root review only; not submitted.** This is a separate retry bundle. The frozen R1 payload and its failed run remain unchanged. R2 asks for one node, four CPUs, 16 GiB and six minutes with zero GPUs and no model weights.

## Why retry

Actual job 27387 failed with scheduler exit `124:0` after 93 seconds. Its retained JSON says `FAIL_TIME_LIMIT_OR_SIGNAL`, has no completed fixture cases, and does not record native Enroot cleanup. The host receipt shows container creation consumed 76 seconds (epochs 1793289633–1793289709); PyTorch import then took 2.142 seconds, leaving roughly 12 seconds before R1's absolute batch-start+90-second process deadline. This is evidence that R1's deadline was too short for cold JIT after container creation. It is **not** evidence that the compiler or C++ implementation is unsupported.

R2 retains the same image, exact source excerpts, CPU fixture, page sizes, numerical invariants, `MAX_JOBS=2`, `OMP_NUM_THREADS=2`, and private cold `TORCH_EXTENSIONS_DIR`. It adds two CPUs to give Enroot and host setup a four-CPU cap, and increases the bounded allocation from two to six minutes. This is a bounded retry after observing the 76-second setup cost, not a change to an owner-set GPU or SU budget. Reservation: zero GPUs, zero GPU-hours, zero PBS SU; maximum CPU reservation is 0.4 CPU-hours.

## Deadline and cleanup design

The absolute fixture deadline is batch-start+300 seconds. The container runs `deadline_runner.py`, which starts the probe in a new process group, signals the whole group at the deadline, allows 15 seconds to reap it, then sends KILL if required. The runner writes a deadline receipt and preserves partial result JSON. Unlike R1, the outer batch does not wrap `srun` in `timeout`; after the inner supervisor exits, the native runner's normal wait/EXIT path removes its own job-specific Enroot rootfs. The six-minute scheduler wall limit leaves up to 60 seconds after the absolute process deadline for finalization and cleanup.

The copied native runner is pinned in this bundle and caps `ENROOT_MAX_PROCESSORS` at the four allocated CPUs. Its cleanup marker is emitted only when the exact per-job rootfs and data directory are gone. A cleanup failure makes the launcher fail and cannot be counted as a passing preflight. The pre-existing R1 path `/tmp/apacsc42-native-27387-0` is not touched by this R2 job; it is a separate exact-path cleanup item requiring proof of terminal R1 state and no live process on original host `g1` before any removal.

## What the probe checks

Inside the pinned native image, the probe confirms CUDA is unavailable, records Python/PyTorch/compiler/Ninja versions, verifies the exact C++ runtime source both before JIT and after module import, records the built extension path and hash under a private extension cache, then runs CPU `int64` radix-tree fixtures for page sizes 1 and 16. Page 1 is the production-page-size fixture; page 16 is metadata-only and does not qualify page-16 KV behavior. No Qwen weights, model server, GPU, serving load or performance measurement is involved.

A pass would only establish cold extension build and these isolated CPU data-structure invariants. It would not qualify full `RadixCacheCpp` allocation, eight P ranks, P/D ownership, Qwen output quality, competition score or speed. Any R2 pass still requires a separate reviewed full-model startup and semantic trial before benchmarking.

## Bundle contents

- `probe.py`: exact R1 fixture and numeric invariants, unchanged.
- `deadline_runner.py`: absolute-deadline process-group supervisor and result receipt.
- `native-container.sh`: pinned per-job Enroot lifecycle wrapper with four-CPU cap and verifiable cleanup.
- `job.sbatch`: six-minute, one-node, four-CPU, 16-GiB, zero-GPU prepared request.
- `evidence/`: source excerpts used to compare the runtime image before and after JIT.
- `validate.py`: local mutation and dry-run checks; no Torch, model, CUDA, scheduler or network runtime.

No scheduler receipt, job ID, runtime result or C++ build outcome exists for R2. Submit only after root reviews the frozen hashes, validation output, queue and resource reservation.
