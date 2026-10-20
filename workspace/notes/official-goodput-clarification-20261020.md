# Official ranking units: Goodput multiplied by 200

Recorded on 2026-10-20T12:46:40.317494+00:00. Source: the owner pasted a discussion in this chat attributed to Pengzhi Zhu replying to Hirotaka Tsuneki. No message URL or original calendar date was supplied; this is retained user-provided clarification, not an independently fetched chat transcript.

The reply explicitly selects **Goodput × 200**, reading Goodput from `profile_export_aiperf.json`. Goodput is measured in requests per second; multiplying by the fixed 200 output tokens per request converts it to good output tokens per second. Because every candidate is multiplied by the same positive constant, rankings are unchanged.

For example, 100 requests over a ten-second measurement with 90 qualifying requests gives 9 good requests/s and 1800 good output tokens/s. Actual AIPerf phase timing remains authoritative; do not substitute a nominal duration for the exported metric. A good request passes both TTFT and ITL conditions (3000 ms and 20 ms in the retained contest protocol). Errors remain failures in acceptance accounting. The minimum 90% passing-request gate is separate from maximising Goodput. Passing latency conditions is not a certification of answer correctness; the organiser model-quality gate remains separate.

Use the exported `goodput.avg` in the retained JSON schema and multiply by 200. Do not multiply it by the passing-request fraction again: Goodput already counts qualifying requests. Do not replace the stated official formula with raw output token throughput multiplied by the passing fraction; equality depends on matching token counts, request populations and time intervals, and the supplied clarification specifically instructs reading Goodput.

## Existing implementation check

The active retained `nscc-pbs/h100-prefill-rr-n54-control-70/summarize.py` reads `goodput.avg` and assigns `good_output_tokens_s = goodput * 200`. The stricter `serving-tuning/review-n54.py` also returns `good_tokens_s = values['goodput'] * 200` after validating the measured phase interval and request counts. Their formulas agree with this clarification; no scorer or frozen payload was changed. This is a targeted implementation check, not a new audit of every historical run.

The retained H200 result 3022.034919 good output tokens/s therefore corresponds to approximately 15.110175 good requests/s. This unit conversion adds no performance improvement and does not verify official full-set model accuracy.
