# Exact-token diagnostic prepared; gateway capability remains a runtime gate

The native SGLang chat endpoint can return actual generated token IDs when
`return_token_ids=true` and `stream=false`. Its response builder copies
`output_ids` into each choice's `token_ids`; it can also return the input IDs.
Streaming requests with this extension are explicitly rejected. This gives a
concrete observation route for the proposed EAGLE3 correctness pilot, separate
from the unchanged streaming AIPerf scoring command.

## Source evidence and remaining uncertainty

The three native Python files and extraction hashes are retained in
[token-interface-extraction.json](token-interface-extraction.json).
`serving_chat.py` checks the nonstreaming requirement near line 914 and builds
the token-ID response near line 1819. These are inspected image source files,
not a successful request or a loaded model.

The image's HTTP PD router serializes its typed request before injecting
bootstrap fields. Its nonstreaming response path returns the decode response
bytes directly when logprobs are disabled. Thus the response path appears able
to preserve the extension, but the typed request schema is still a potential
filter. The gateway library reexports `openai_protocol` and its Cargo manifest
declares version `=1.0.0`; the protocol definition is not under the guessed local
`src/protocols` paths. That extraction returned zero files despite exit status
zero. A public crate download attempt failed DNS resolution for
`static.crates.io`; no crate source was fetched or validated. Do not infer
support from a newer online API version or from worker support alone.

The retained gateway source and receipts are in
[gateway-token-extraction.json](gateway-token-extraction.json) and
[gateway-module-extraction.json](gateway-module-extraction.json). A future
allocated pilot must first send a request through the actual gateway and fail
if actual prompt/output IDs are absent. Do not bypass the gateway, infer IDs by
retokenizing decoded text, or modify a running scored job to probe this.

## Prepared diagnostic and acceptance sequence

[token-equivalence.py](token-equivalence.py) prepares four generic, unranked
greedy requests: arithmetic, code, explanation and Unicode punctuation. Requests
use temperature 0, top-p 1, seed 2026, a 200-token maximum and nonstreaming actual
ID return. They are a small integration test, not the contest dataset, exact
4000-token workload, long-context validation or official accuracy evaluation.

In a separately derived allocated pilot:

1. Retain a stable target-identity manifest containing the official weight,
   configuration and tokenizer digests. Supply that same manifest to each
   capture; the helper checks its digest but does not validate its contents.
2. After target-only readiness, capture `target-a` and `target-b` through the
   gateway. Compare actual prompt IDs, generated IDs and finish reasons. A
   mismatch means the target reference is unstable under these conditions;
   investigate before attributing later differences to speculation.
3. Enable the draft in a separate stage with the same target, platform,
   requests and control settings. Confirm real draft class/parameter loading,
   unquantized BF16 draft precision, feature capture, patched heterogeneous
   TP4-to-TP8 state/transport geometry, kernels, graphs and memory headroom.
4. Capture `draft` and compare against `target-a`. Any missing IDs, failed
   request, changed input, invalid token or output/finish mismatch blocks
   correctness acceptance. Preserve partial responses and the first mismatch.
5. Only a valid integration merits long-context checks and a short unranked
   load screen, followed by a full matched scoring pair if the screen is useful.

The helper has a 90-second request timeout, four sequential requests, bounded
response size, no retry and exclusive output creation. It has not been invoked
against a live model. Thirteen adversarial CPU fixtures pass, including equal
decoded text with different IDs, absent IDs, changed prompts/seeds/platforms,
truncated outputs, invalid IDs and changed finish reasons. See
[validation](token-equivalence-validation.json). These fixtures test the
diagnostic's rejection behavior; they establish no model equivalence or speedup.

No speculative GPU job or SU reservation was added for this checkpoint. The
five H200 queue positions remain occupied. H100 is running the independent
CPU-envelope control/candidate pair. Preserve the original preflight and staging
indices unchanged; this followup has a separate evidence index.
