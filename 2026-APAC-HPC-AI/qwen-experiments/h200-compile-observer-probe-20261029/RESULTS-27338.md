# 27338 failed before compilation: contextmanager source inspection bug

Reviewed 29 October 2026, Vietnam time (UTC+7). Actual scheduler state is **FAILED 1:0**, elapsed **76 seconds on g4** using one H200. This is not a successful fixture, compile result, model startup or performance measurement.

The native launcher and exec.rc hashes pass, the exact frozen files pass, one H200 is visible and the container starts. Before setting up compilation or allocating the tiny model, the observer checks `inspect.getfile(decoration.patch_model)` against the pinned SGLang module hash. It obtains `8b7a477f978a8532852fd81e241c78182516bc4975d672d580a5848a76e11eb6`, not the expected `77b1e38dba14788800b6b6351af1b5b8a80d9e42b91b57e9484ea4561d33a48c`, and correctly fails closed. Runtime results is empty. No Qwen weights or compiler/capture traffic ran.

Pinned source inspection identifies the first hash as `/usr/lib/python3.12/contextlib.py` from the same image. SGLang's `patch_model` is decorated with `@contextmanager`; that decorator returns a wrapper defined in contextlib. `inspect.getfile` sees the wrapper's code file, whereas `inspect.unwrap` can recover the original SGLang generator. The SGLang module itself still matches the expected pinned hash. This is an observer source-location error, not evidence that compilation or the target model is incompatible.

A derived R2 must compare the actual module file and unwrapped generator file, require both to identify the same source, and keep the exact same expected hash. Do not bypass the pin or edit this submitted bundle. A successful R2 would still establish only the tiny observer/PyTorch capture interface, not production Qwen/HPC-Ops/eight-rank startup or useful performance.

Native logs show command exit 1 and cleanup begin/end. Allocation occupancy is 76/3600 = 0.021111 GPU-hours, distinct from the maximum 0.066667 reservation. No PBS SU. Original raw error, source, receipts and terminal accounting are preserved in raw-seal-27338.json. The source-location diagnosis and corrected code belong in the separate R2 directory and require a new definite admission before being called submitted.

The original admission STATUS.md used a pending sentence even though the queue captured at publication already showed RUNNING. That sentence is superseded by this actual terminal accounting; preserve the dated queue text and correct the current handoff. Original frozen README/job/probe/provenance and their manifest are unchanged.
