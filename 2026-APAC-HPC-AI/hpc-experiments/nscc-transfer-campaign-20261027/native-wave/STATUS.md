# Native first wave: reviewed offline, access blocked

Updated 2026-10-27T10:58:19.047506+00:00. **No PBS submission or reservation exists for this bundle.**

- Frozen payload: 61 files; root independent offline review passes.
- Arms: default Scotch, hierarchical xyz, hierarchical zyx.
- Hardware request: four exclusive CPU nodes, 512 ranks, 90 minutes, zero GPUs.
- Work: complete mandatory initialization and 150 solver steps per arm; 149 timer samples each.
- Maximum request cost: 768 SU at the verified historical rate 1; fresh rate and credit still gate admission.
- Active blocker: fresh admission precheck returned BLOCKED because no live VPN tunnel was available. Two authorised login attempts returned Authentication failed; the owner reported a pending DUO notification but immediate approval is not confirmed. No repeated login loop is running.

## What passed

Root independently reran native source/sequence/negative-edit checks and all 9 admission budget/queue/idempotency tests. The actual retained NSCC Scotch and hierarchical decomposition logs pass the new fixed-cell parser. The actual retained solver host list matches its PBS nodefile; a wrong host fixture is rejected. Root added actual native solver-host checks, deterministic runtime hashes with an equality gate, frozen sequence selection, separate field-seal/log paths, and bounded time/space preflights. [Exact root review](ROOT_REVIEW.json).

These checks do not prove real new runtime success, a score, or a gain. S0 improving against an older S0 measurement would be a new control observation, not credit for a new optimization. Judge hierarchy candidates against the fresh S0 and exact xyz/zyx comparison, retaining all timed steps.

## Execution when access is verified

From the campaign root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 campaign/admission.py precheck
PYTHONDONTWRITEBYTECODE=1 python3 campaign/admission.py deploy
PYTHONDONTWRITEBYTECODE=1 python3 campaign/admission.py submit
```

Run sequentially and proceed only after each command passes. Submit rechecks hashes, both queues, selected CPU project, current credit and all existing reservations under CPU-before-AI locks. It writes one durable intent and reserves 768 SU before one qsub. Any uncertain receipt blocks retries until reconciled; it never launches automatically. Existing four shared-account CPU jobs from the old snapshot require current ownership and reservation review.

After terminal status, `campaign/collect-native.py` retains small logs, original case inputs, output tables, seals and manifest without processor meshes/fields or runtime caches. Its archive hash/member integrity check does not replace a scientific run review. No real new run has been collected yet.

The author draft review/seals are retained separately; ROOT_REVIEW and the current payload seal describe the final root corrections. Existing submitted bundles remain unchanged.
