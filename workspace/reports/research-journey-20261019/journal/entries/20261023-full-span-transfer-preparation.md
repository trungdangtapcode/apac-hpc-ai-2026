# Production-span transfer hypothesis: preparation

23 October 2026; preparation only, before a GPU submission.

## Question and prior evidence

Native probe 223132 transferred small synthetic buffers. Full-model 223788 independently observed 190 KV regions of 76,132,096 bytes each and ten auxiliary spans, but ended at our unsupported explicit-layer-ID gate before transferring requests. The source-order review found no final pointer reorder in the current PP=1 path. Large registered ranges and valid source arithmetic still do not prove live byte transfer.

## Hypothesis and controlled experiment

Exercise the same pinned native registration, heterogeneous-TP selector and request-scoped send methods on two actual H100 GPUs across two hosts, without model weights. Reproduce all 190 full-size GPU allocations (14,465,098,240 bytes per rank) and ten exact pinned-host spans. Send two sparse pages per region: source 1/297390 to destination 0/297389, each 256 bytes. Validate all 380 distinct payloads and scan all other destination bytes on GPU. Independently verify the source remained intact. Test whole auxiliary spans as one diagnostic item each; native per-request auxiliary strides remain unknown.

## Preparation findings and correction

Root found that the initial unsubmitted preparation patterned both endpoints. It would contaminate the destination's untouched-span baseline and prefill expected auxiliary data, concealing a missing auxiliary transfer. The corrected payload patterns only the sender. A sparse CPU fixture exercises the actual destination verifier and rejects the reproduced contamination. Five CPU test functions, pinned source/role-order fixtures, Python/shell syntax and frozen checksums pass. Full GPU execution remains untested. Preserve this preparation mistake as a test-design lesson.

## Cost, limits and decision

At most two H100 GPUs for ten minutes: maximum 42.666667 SU under the existing AI budget cap 51000 SU and project reserve 13000 SU. Submission must recheck selected AI queue and credit under the budget lock. The current 4550.370 SU internal headroom can cover it; no reservation exists at this preparation checkpoint. H200 correctness job 25682 remains queued unchanged. A pass would establish only this two-rank transfer geometry, not all-rank serving, EAGLE output correctness, official accuracy or a speedup.

[Plan and frozen source](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/nixl-production-span-probe-20261023/PLAN.md).

## Explanation for a presentation

“Registering memory tells the transport which addresses it may access. It does not prove that the intended bytes arrive. We therefore test production-sized memory with uniquely marked pages, then verify both the received data and every byte that should stay unchanged. We do this without loading the model to reduce cost.”
