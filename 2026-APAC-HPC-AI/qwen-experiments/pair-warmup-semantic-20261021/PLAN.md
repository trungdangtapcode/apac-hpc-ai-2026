# Semantic P/D warmup gate (prospective)

The frozen R3 warmup currently treats any nonempty `choices` array as success, and the topology wrapper prints `ALL_PAIRS_WARM` immediately after the remote step returns. A PBS shim can mask a failed remote task, so that marker alone does not establish that all endpoint pairs produced usable completions.

This derived stdlib-only helper validates each HTTP 200 response for nonempty assistant text and consistent `prompt_tokens`, `completion_tokens` (1–8), and `total_tokens`. It creates one atomic receipt per unique pair from the Cartesian prefill/decode inventory. Receipts bind the canonical inventory SHA-256 and a fresh 32-character run token. The small raw HTTP status and completion JSON are retained separately, without headers or authentication data. The head checker reparses the real body and recomputes its semantic counts and hashes, so a receipt cannot pass by reporting plausible counts alone. The final checker rejects missing, duplicate, stale, malformed, or route-mismatched receipts.

For a future derived topology bundle, create a fresh run token for that invocation, pass it to the remote warmup, and after the remote step returns run `python3 warmup_semantic.py --check --endpoints "$ART/endpoints.tsv" --receipt-dir "$ART/pair-warmup-receipts" --run-token "$QWEN_PAIR_RUN_TOKEN"`. Print `ALL_PAIRS_WARM` only if this head-side check succeeds. Do not rely on the remote step's own success marker. A model HTTP 500 or invalid JSON/usage fails immediately; only the existing bounded 503 worker-registration condition retries.

The prompt, temporary per-pair router, `max_tokens=8`, and `temperature=0` remain unchanged. This is a prospective semantic gate and does not establish transport reliability, model equivalence, or correct remote exit propagation by itself. The CPU tests exercise parsing, receipt binding, malformed responses, and success-marker gating without claiming to reproduce GPU/network behavior.

No existing frozen payload is changed. These are prospective CPU-validated files only. Deployment, GPU behavior and full-model correctness remain unverified. The run token is an experiment identifier, not an authentication credential.

For PBS clean-container dispatch, pass the experiment identifier explicitly with
`env QWEN_PAIR_RUN_TOKEN="$QWEN_PAIR_RUN_TOKEN" python3 "$BUNDLE/warm-topology.py" ...`.
The allocation head must retain that same identifier and run the independent
checker after the remote step, before printing its success marker or launching
the exact-token client. Generate the identifier once with `uuid.uuid4().hex` for
each fresh invocation. A successful scheduler or remote-shell return does not
bypass the head-side checker. The current R3 bundle remains unchanged.
