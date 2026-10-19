# Validate the graph configuration derived from the changed chunk

The first strict review held job 221828 because changing prefill chunk4096 to 6144 also changed the resolved prefill graph maximum and capture buckets. This was an unrecognised derived runtime field, not evidence that the GPU run or output failed.

The exact retained SGLang server_args.py sets the non-MLA prefill graph maximum from chunked_prefill_size and generates the buckets with _generate_prefill_cuda_graph_batch_sizes. The reviewer now verifies the source hash, evaluates that isolated pure generator, validates the old/new bucket lists and maximum, and then requires every other AST field in the graph configuration to remain identical. Decode and prefill graph backend/compiler settings cannot change under this allowance. No submitted payload, benchmark, model, precision or quality checks are modified.

The initial held review is retained in 221828-initial-review.json. Corrected classification is produced only after every other full protocol, runtime, frozen payload, request/SLA/error, short and 12-long-output gate still passes. The derived graph effect is part of changing the chunk; this is not a chunk-only causal result with graph shape held fixed.
