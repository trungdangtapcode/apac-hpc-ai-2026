# H200 target-reference draft review

This report covers the isolated, unsubmitted draft in `mutable-proposal/payload`. No scheduler command, allocation, budget update, shared note, archive capture or submission was made.

## Changes reviewed

- `topology-job.sh` now verifies the exact two-TP4-prefill / one-TP8-decode placement before launching workers. Each worker log must contain every expected BF16 KV allocation record in the real timestamped TP format; the decode records must include matching TP and EP ranks. A generic TP string or partial rank set fails closed.
- The launcher passes the experiment identifier, absolute client deadline and image path explicitly through worker, router, pair-warmup and token-client container commands. The checker is bounded by the remaining 20-second result-check stage. Failure cleanup waits at most 40 seconds from the failure and is capped by `T0+990`; the absolute `T0+1020` allocation guard remains.
- `token-control.py` records weight names and byte sizes, small metadata hashes, and the runtime image path and available byte size. Full model-weight and image hashes remain explicitly uncollected. `check-token-result.py` independently verifies the exact request fields for all eight records.
- `validate-cpu.py` adds real client execution against a local mock HTTP server, rank-parser fixtures, independent malformed-result rejection, and an execution fixture for the actual shell launcher with a failed token client. The inherited NIXL source bytes and checksum file remain preserved under their native provenance names.

## Validation results

- `validate-cpu.py` passed under Python 3.9. It accepted the complete two-pass 1600-ID fixture and rejected 199-token, missing, duplicate and invalid-ID output; wrong input/request fields; wrong finish semantics; pass mismatch; false pass state; and incomplete or generic-rank BF16 log evidence. The mocked actual client accepted the valid endpoint and rejected each malformed response. The launcher fixture observed client exit 7, a failed launcher result and prompt cleanup.
- The independent `pair-warmup-semantic-20261021/CPU-test.py` suite passed under Python 3.9.
- Python 3.9 AST parsing passed for all payload Python files; `bash -n` passed for the shell and Slurm files.
- `prepare.py` verified every current `SOURCE_SHA256SUMS` entry, the source pins, the frozen corpus digest, and the retained native checksum manifest. It reported 23 payload files and corpus SHA256 `8022c00013d5b5f022e959af9fbffb017a164113e2c909fd8d11ef3e76c25dd7`.

## Remaining review risks

- The corrected parser passes all 16 expected ranks on retained sealed H200 job 25373 logs. This validates the current production log format; the proposed reference job has not run and must pass the same startup gate itself.
- Startup within 600 seconds, semantic warmup against live endpoints, NIXL operation, exact output IDs and model/image identity remain unverified. CPU fixtures do not reproduce GPUs, multi-node networking or model serving.
- Available file names and sizes help identify staged assets but do not prove identity. Full large-weight and image hashes were not collected; reviewing-agent verification against current cluster bytes remains a freeze gate.
- No per-rank KV geometry, pointer, peer metadata or transport hook was added. Those measurements remain not collected.

The proposal remains a target-only exact-token reference preparation. It is not an EAGLE3 run, score, official accuracy result, performance result or submitted payload.

## Root-review correction: native BF16 log suffix

Root review replayed the proposed parser against the retained sealed `runs/25373` logs and found that its initial expression stopped at `torch.bfloat16`. The native SGLang records continue with token capacity and K/V sizes, so the initial gate would have rejected every real rank line. This was a parser defect; the underlying H200 logs were unchanged.

The parser now requires the complete native suffix: a positive integer token count plus positive numeric K and V sizes in GB. It preserves the role-specific TP and TP/EP tag rules. Direct Python 3.9 CLI checks against the sealed `prefill-0.log`, `prefill-1.log` and `decode-0.log` now pass for ranks 0–3, 0–3 and 0–7. The retained values are 1,531,197 tokens and 34.32 GB per K/V pool for each prefill rank, and 2,148,119 tokens and 48.14 GB per K/V pool for each decode rank.

Replay on temporary copies of the sealed decode log rejected each of: a malformed `K size` suffix, a missing TP7/EP7 allocation line, and a TP3/EP2 mismatch. The first mismatch mutation attempt changed an earlier unrelated TP3/EP3 string elsewhere in the log and therefore did not exercise the gate; the final replay targeted the allocation-line prefix specifically, and the CPU fixture now does the same. The Python 3.9 fixture uses production-shaped allocation lines and covers malformed suffixes, zero token count, missing ranks, and mismatched EP tags. This remains log-format validation only; it does not turn the dated 25373 snapshot into a claim about future H200 startup.
