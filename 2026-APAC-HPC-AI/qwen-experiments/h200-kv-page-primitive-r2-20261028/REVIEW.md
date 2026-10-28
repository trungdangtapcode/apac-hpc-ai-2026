# Slurm 26990 failure review and R2 diagnostic

Recorded 2026-10-28. Original submission `h200-kv-page-primitive-20261028` and its run artifacts are preserved unchanged.

## Observed failure

Slurm job 26990 exited with status 1 in the first numerical case, TP4/page1/length15. The exact assertion was the predeclared combined oracle check: relative L2 `0.0019173745531588793` (within `0.01`) and maximum absolute error `0.007483720779418945` (above `0.005`). The traceback points to the numerical assertion after exact cache-write checks and FlashInfer output shape, dtype and finite checks. The run stopped before appending any case, so no later geometry or boundary was inspected. This establishes an unmet oracle threshold in that case; by itself it does not establish a page16 defect.

The oracle is computed in FP32 from BF16-rounded Q/K/V, while the FlashInfer output is BF16. The submitted maximum-absolute threshold did not account explicitly for output quantization. That is a plausible explanation to investigate, not a demonstrated root cause: the original output tensor was not retained, and the result file contains no BF16-rounded-oracle comparison. No threshold is retroactively relaxed.

## Derived R2 diagnostic

R2 keeps the strict FP32-oracle limits (`relative L2 <= 0.01`, `maximum absolute <= 0.005`) as per-case diagnostic flags and attempts all 28 cases. It additionally records output differences against the same FP32 oracle rounded to BF16, plus maximum local BF16 ULP ratio. These measurements distinguish an output-representation-sized discrepancy from a larger backend/oracle disagreement. Page1-versus-page16 errors remain recorded. Any non-numerical setup, native write, shape, dtype, or finiteness assertion still fails closed.

The final state is deliberately `DIAGNOSTIC_COMPLETE_NO_PASS_CLAIM`; R2 does not turn the earlier failure into a pass or broaden production geometry exceptions. Results must be reviewed before setting any acceptance criterion for a new correctness run. No job has been submitted.

## Static checks

AST parsing, Python bytecode compilation, shell syntax checks, and payload hash generation were run locally. These do not validate GPU execution or scheduler acceptance.

Root review adds explicit TF32-disabled FP32 oracle arithmetic and records the worst-error output, FP32 reference, rounded BF16 reference and local representable step per case. This avoids inferring quantization solely from aggregate error. Runtime checks the frozen manifest before allocation work. No original thresholds change and diagnostic completion is not correctness acceptance.
