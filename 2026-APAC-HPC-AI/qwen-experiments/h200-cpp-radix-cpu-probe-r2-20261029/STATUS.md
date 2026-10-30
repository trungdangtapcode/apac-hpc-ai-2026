# R2 status

**Prepared, not submitted.** The frozen R1 attempt is retained as a failed diagnostic, not a C++ compatibility verdict. R1 job 27387 exited `124:0` after 93 seconds. The actual host timing shows 76 seconds in Enroot creation and approximately 12 seconds remaining after PyTorch import before the batch-start+90-second deadline. R1 had no completed radix fixture and no native cleanup marker.

R2 changes only the diagnostic resource/time envelope and deadline/cleanup supervision: one node, four CPUs, 16 GiB, zero GPUs, six-minute Slurm wall limit; absolute batch-start+300-second fixture deadline plus up to 60 seconds for cleanup. The cold source-pinned extension build and page-1/page-16 CPU invariants remain the same. A CPU JIT timeout remains a failed preflight. This does not authorize or imply the later 16-GPU S106 candidate.

See `README.md`, `READY.json`, and `VALIDATION.json`. Await root review; no receipt or result exists.
