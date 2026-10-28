# Portable AIPerf artifact path fix

Prepared 29 October 2026 as an isolated integration candidate. Job 27136's actual AIPerf run completed, but its local Slurm step ended with exit code 1 because the gate and summary reader assumed the two exports were directly under `artifacts/`. The actual pair is under `artifacts/qwen-openai-chat-concurrency64/`.

`artifact_paths.py` resolves the complete pair only at the artifact root or one immediate child. It rejects missing, incomplete, ambiguous and symlink namespaces, and does not recurse through phase trees. `score-gate.py` and `summarize.py` are copies of the frozen replay scripts with only this path-resolution integration. Their benchmark invocation, limits and score calculations are unchanged. The submitted and published files, including job 27136's frozen payload and raw terminal evidence, were not edited.

## Verification

Against the retained raw job 27136 directory:

- The patched score gate passed: 1,906 requests, 1,880 good requests, 98.6358867% joint SLA, zero errors/cancellations, 3,050.225487 good output tokens/s (`goodput.avg * 200`). Official accuracy remains unverified.
- The patched summary reader emitted one `official` row from the nested namespace, retaining the raw throughput and latency metrics.
- Eight targeted tests passed: legacy flat and nested pairs, ambiguous/incomplete/missing pairs, symlink escape rejection, an injected bad request rejected by the score gate, and summary over both legacy and nested layouts.

These checks validate the corrected local readers. They do not change the actual scheduler receipt: job 27136 remains a terminal failure with exit code 1. Its original failure record and raw outputs remain intact. This candidate has not been integrated into a published submission or submitted to a scheduler.

## Files

- `artifact_paths.py`: bounded, safe export-pair resolver.
- `score-gate.py`: isolated copy patched to use the resolver.
- `summarize.py`: isolated copy patched to use the resolver.
- `test_artifact_paths.py`: focused resolver, gate and summarizer regression tests.
- `SHA256SUMS`: hashes for these five reviewable files (excluding the hash file itself).

Root review additionally binds the summary client log to the run directory rather than the selected export parent; the flat/nested fixture now checks cancellation counts from that log. This prevents nested namespaces from silently losing phase-completion evidence.

## Second real replay: compute mount alias correction

27145 completed the official GPU client but ended1:0 while summarizing: the resolver returned canonical /scratch/home paths while the summary calculated relative paths against lexical /home. The root is now canonicalized consistently; new assertions cover an absolute mount alias and a relative alias. Original27145 files stay unchanged. Validate both retained raw runs on an actual compute CPU job before spending another full GPU allocation on this reader.
