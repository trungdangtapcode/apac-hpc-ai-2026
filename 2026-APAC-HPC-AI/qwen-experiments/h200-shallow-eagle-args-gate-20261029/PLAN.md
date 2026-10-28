# Shallow EAGLE3 argument policy gate

Prepared 2026-10-29. This is a bounded source-policy prerequisite for a distinct decode-only EAGLE3 candidate using `--speculative-num-steps 1`, `--speculative-eagle-topk 1`, and `--speculative-num-draft-tokens 2`. The unchanged 2/3 branch remains closed.

## Evidence checked

`check_source_policy.py` verifies the retained native `server_args.py` and `arg_groups/speculative_hook.py` SHA-256 values against the native source receipt, confirms the required `ServerArgs` fields exist, and checks the exact top-k=1 rule in `_handle_eagle_family`: draft tokens are adjusted to `steps + 1` only when the supplied count differs. The proposed 1/2 pair is canonical and therefore does not enter that adjustment branch. Result: `source-policy-result.json` (`PASS_SOURCE_AST_POLICY_ONLY`).

## Scope limit

This is static policy evidence, not an invocation of the native CLI parser or construction of `ServerArgs`. It does not prove algorithm dispatch, exact resolved `ServerArgs`, path/config metadata validity, draft dtype/quantization resolution, one-GPU availability, or TP8 distributed operation. It performs no model or tensor loading, CUDA work, P/D setup, KV/NIXL registration, semantic check, output check, or performance measurement. No TP8 multi-rank pass is claimed.

The next useful bounded step, if admitted, is one H200 GPU / eight CPUs / four minutes running only the pinned-image `ServerArgs.add_cli_args` parser on decode flags with `tp_size=8`, `ep_size=8`, BF16, EAGLE3 top-k 1, steps 1, draft tokens 2, FlashInfer draft attention, unquantized draft, and the frozen draft path. It must assert the raw parser values exactly, verify the visible device count is exactly one, and label itself parser-only; it must not instantiate a model or claim TP8 feasibility. If native imports/constructor require distributed state, stop and retain this source-only result. No job has been submitted.

The future full candidate must still derive from S93, reuse matched control 26949 with exact pairing, and separately gate actual runtime/KV/graphs, P/D semantics, workload/output checks, and local quality evidence. Existing strict 1600-ID failures remain; official accuracy remains UNKNOWN.
