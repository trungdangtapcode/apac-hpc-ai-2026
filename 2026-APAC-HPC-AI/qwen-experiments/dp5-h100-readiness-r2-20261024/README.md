# Correct the D5 prospective source manifest

The parent H200 job25921 stopped before model load because one character in the expected server_args.py hash was wrong. Direct CPU extraction from the pinned image proves retained source bytes match the image; the source code did not change. The other12digests match. The pending H100 parent224552 was cancelled before allocation to avoid the same known error. This derived R2 corrects the metadata, preserves all startup acceptance gates and moves observer imports after preflight. No successful D5 GPU outcome exists yet.

See R2_ROOT_REVIEW.json, parent seals and the source correction audit. Five assigned GPUs,17minutes; H100 maximum181.333333SU. A health pass without all-rank map/dtype/loaded-copy evidence is rejected. No generation or performance stage.
