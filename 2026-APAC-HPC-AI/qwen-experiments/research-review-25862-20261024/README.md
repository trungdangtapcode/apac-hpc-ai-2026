# S49 H200 EAGLE3 job 25862 review

Job **25862** ended `FAILED` / `1:0` after 00:09:17. Failure is localized: startup, deterministic runtime, all-rank BF16/NIXL, 190-region geometry, both semantic P/D receipts, request equality, and candidate repeat stability pass. The strict exact-target-ID gate fails for all four cases. Both 200-token EAGLE passes match each other, but each differs from accepted target job 25855. First zero-based ID divergences are arithmetic 138, code 12, Unicode 11, and long4000 61. All finish with `length=200`. The 1,600 EAGLE output IDs and candidate/reference comparisons are retained. This is a local exact-reference failure, not an official model-quality or accuracy verdict.

The head checker fails because the exact-ID comparison sets `passed=false`; this does not invalidate independent readiness receipts. Responses contain selected-token log probabilities and native speculative counters, but no alternate/top-two logits or margins. A bounded source-based numerical hypothesis is a shape difference between EAGLE target-verify batches and ordinary one-position target decode. The pinned source paths support that hypothesis, not causation. No GPU retry was made.

Resolved runtime comparisons, per-case latency, acceptance counters, telemetry, and source hashes are in [REVIEW.json](REVIEW.json). Pinned source identity and file hashes are in [SOURCE_PROOF.json](SOURCE_PROOF.json); independent scheduler receipt is [accounting.psv](accounting.psv). Actual run artifacts are sealed with SHA-256 `651e3f5bd86c38a8d0056ca9867382c6920aa104cdf2a21fd07c50c956298b33`.


Observability limits: response-level queue time is retained, but role-level queue depth, batch size/in-flight timelines, and KV token occupancy were not collected. Bounded GPU sampling includes startup/shutdown zeros and transient metrics-endpoint `URLError` polls; it is not evidence of stable memory utilization or a causal bottleneck. Both jobs used the same pinned container image hash.
