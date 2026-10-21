# Actual-runtime corpus gate passes: 222759.pbs111

Sealed F / exit 0, **58 seconds**, estimated **2.062222 SU**, reviewed 2026-10-21T05:16:42.547267+00:00. Submitted payload hashes and raw evidence seal pass. This probe performs CPU-only tokenizer work in a one-GPU allocation; no target/draft weights, inference, GPU operations or performance measurement.

The actual image has **Transformers 5.12.1**, Qwen2Tokenizer. Explicit return_dict=False returns plain lists for all three short prompts; the defensive Mapping normalization and JSON roundtrip remain required. Exact lengths are **22 / 21 / 22 / 4000 input tokens**. All IDs are valid target-vocabulary integers and the complete four-case corpus serializes successfully. Verified official small-file digests and actual tokenizer source hash are retained in collection.json.

This resolves the concrete tokenizer/corpus issue before another 16-GPU startup. It does not establish actual gateway output-ID completeness or greedy reference stability. Freeze the verified cases into a new full target-only repair, remove AutoTokenizer from that expensive client, and independently require the semantic passed artifact in the allocated head script. Retain failed 222752 and all original payloads. No speculative candidate is yet eligible.

[Collection](collection.json), [sealed hashes](collected/222759.pbs111/evidence-sha256.json), [fixture checks](validation.json).
