# Current token observation route and historical correction

The earlier preflight TOKEN_IDS.md described a proposed nonstreaming chat return_token_ids route, with explicit unverified typed-gateway behavior. Actual 222721 proves the native gateway filters those flags and does not return the requested actual IDs. That old helper is not a working full-PD correctness route. Preserve its historical source/tests rather than silently repurposing it.

222722, 222729 and 222749 establish actual native /generate forwarding and synthetic logprob-ID preservation. Those IDs are deliberate mock markers, never generated model outputs. Real response completeness, including the first prefill-generated token, still needs the separate full target-only control 222752.

The new token-control.py requests native /generate using actual target-tokenizer input IDs, return_logprob=true and sampling_params.sampling_seed=2026 (the inspected native field), then requires output_token_logprobs to contain all completion_tokens=200 real IDs. It compares two actual greedy passes, with no retokenization of decoded text, no direct worker bypass and no failed-request retries. These are diagnostic settings outside the unchanged official streaming AIPerf ranking protocol.

222750 independently proves actual native draft class construction and exact non-shared weight loading. That does not prove real target embedding sharing, TP4/TP8 states, KV transfer, attention/CUDA graphs, output equality, useful acceptance, speedup or organiser accuracy. The next candidate remains blocked on valid real reference evidence and a separately frozen integration design. No full-target speculative job has been submitted.

## Actual reference failure and repaired successor

222752 did not establish real IDs: the installed tokenizer returned BatchEncoding and diagnostic/final JSON serialization failed, although PBS reported exit zero. It is sealed and failed, not an eligible reference. The smaller actual-image tokenizer gate 222759 passes with explicit return_dict=False plus Mapping normalization and plain-ID validation. Its frozen corpus is used by the separately derived 222761.pbs111 real target-only repair, which also requires a semantic result artifact in the head script. Actual complete outputs and stability remain pending; the original scored protocol is unchanged.
