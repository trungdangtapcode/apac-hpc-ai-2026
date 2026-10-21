# Frozen-corpus real reference repair receipt

**222761.pbs111**, submitted 2026-10-21T05:17:31.323410+00:00, state **R** at 2026-10-21T05:19:22.495781+00:00. **16 H100 / at most 20 minutes / max 682.666667 SU**. Fresh own queue empty, no dependency. Exact submitted checksums and login asset preflight pass. [Prospective repair and unchanged serving controls](PLAN.md).

The actual-image 222759 corpus gate passes; its exact 22/21/22/4000-token integer lists are frozen into this client. No AutoTokenizer dependency in this expensive client. Allocated head script independently revalidates the actual result artifact, so launcher exit alone cannot pass the reference. Six observation-rejection and failed/missing artifact fixtures pass; worker and NIXL bytes remain unchanged. No terminal real-ID result yet.

Locked credit: Used **43586.876**, Balance **19730.457**, In Doubt **682.667 SU**. Outstanding full maxima: [{"job": "222752.pbs111", "max_su": 682.6666666666666}, {"job": "222759.pbs111", "max_su": 8.533333333333333}, {"job": "222761.pbs111", "max_su": 682.6666666666666}]. Conservative internal headroom **6039.257333 SU** under unchanged 51000 cap/13000 buffer. [Reconciliation](reconciliation.json). Do not release unposted maxima or subtract In Doubt twice. [Dated scheduler evidence](live-receipt.json).

222752 remains a failed reference despite PBS exit zero and is preserved separately. This job has no ranked AIPerf or EAGLE3 performance claim; a speculative candidate still requires a complete sealed reviewed real reference.
