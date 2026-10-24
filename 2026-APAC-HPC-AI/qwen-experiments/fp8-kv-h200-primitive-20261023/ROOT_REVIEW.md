# Root review: H200 FlashInfer FP8 KV primitive

**Status: implementation review draft; no job receipt or GPU result is present.**

## Question and hypothesis

Question: does the pinned image's native FlashInfer decode and prefill API
execute one synthetic E4M3 KV attention case on a single H200 in NHD layout?

Hypothesis: both API calls will return finite BF16 tensors with the specified
shapes and will agree with FP32 attention over the same rounded cache within
2% relative L2 for the fixed seed and two synthetic scale cases.

## Controls and limits

The deterministic CPU oracle uses the lower-right causal mask, seed 2026, and
synthetic K/V scales 1.0 and 0.5. The native FP32 oracle consumes the exact
rounded FP8 cache tensors. Separate comparisons against the original BF16 KV
source report quantization impact and do not gate kernel agreement. No model
weights, model outputs, serving stack, or performance claim are in scope.

The image path and extracted SGLang source hashes are listed in README.md and
the linked source manifest. The source manifest does not provide a digest for
the whole squashfs image or for the installed FlashInfer package; the runtime
version is recorded by the script. Do not claim stronger source provenance
than that evidence supports.

## Runtime evidence (fill only from actual artifacts)

- Slurm job ID / receipt:
- Terminal state and exit code:
- Image path and any verified runtime fingerprint:
- H200 name, UUID, SM capability, visible-device value:
- Python, PyTorch, CUDA, and FlashInfer versions:
- Cases completed (TP/head geometry and scale):
- Decode/prefill shapes, dtypes, layout and finite fractions:
- Same-rounded-FP8 relative-L2 values (kernel agreement):
- Original-BF16-KV relative-L2 values (quantization impact):
- First-call wall time and warm CUDA event time, with units:
- Raw artifact paths and any missing evidence:

## Decision

Pending implementation review and, if approved by the root, one bounded job.
An API error, timeout, unsupported dtype, failed shape/dtype check, non-finite
output, or same-rounded-FP8 relative L2 above 2% is a failed primitive. Preserve
stdout, stderr, and any partial case records. A pass would authorize only a
separate review of scale provenance and any later quality test; it does not
authorize either automatically.
