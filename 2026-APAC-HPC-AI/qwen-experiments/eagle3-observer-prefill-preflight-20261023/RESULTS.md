# Preparation results — no GPU run

**PREPARED_NOT_SUBMITTED.** The draft uses CPU-only observer/schema fixtures and shell/Python syntax checks. It has no PBS receipt, scheduler state, H100 runtime output, or actual metadata receipt.

The separate four-rank fixture accepts a complete synthetic prefill receipt set and rejects missing ranks and changed measured widths. The shared six-test observer suite passes using fake tensors/mocked methods. The native NIXL source hash is exactly `912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f`. These checks establish schema behavior and source-copy identity only.

The next required evidence is a root-reviewed, separately authorized single TP4 H100 readiness probe that produces HTTP 200 health and four actual per-rank metadata receipts plus actual module source reports. No transport or output conclusion follows from this preflight proposal.

## Root submission, 24 October

Root reviewed and froze the payload after six observer CPU tests and the explicit four-rank schema fixture passed. Job **224275.pbs111** was submitted at 03:03:48 UTC, requesting one node / four H100 / at most 15 minutes, a conservative maximum **128 SU**. Fresh checks under the CPU-before-AI locks found both account queues empty; no CPU job was changed. Selected project 59010042 reported Used 46,518.678 SU, Balance 17,481.322 SU, In Doubt 0. The unchanged internal ceiling/reserve leaves **4,353.322 SU** after this reservation. Keep the full maximum until a unique final charge is posted.

The scheduler accepts the job into aiq1; the last immediate state was Q. There is no GPU runtime pass, transfer test, model-output result, or score yet. Preparation-only statements above describe the earlier draft. The exact receipt is `pbs-receipt.json`; root hashes and the uploaded payload are retained.
