# Global protocol check submitted — 19 October 2026

Submitted **221884.pbs111** (instrumented default-protocol N54 control) and **221885.pbs111** (global prefill Simple N54 candidate). Actual verified chain: **221880 → 221884 → 221885**. The attention trial 221880 was running with elapsed 00:06; the two new trials were dependency-held at the 14:30 UTC check. H200 retained its five earlier pending jobs.

Both new trials enable the same prefill NCCL INFO/INIT/ENV/TUNING logging and Torch NCCL version readout. Their worker files differ only in the candidate's global prefill NCCL_PROTO=Simple line. Decode, precision, transport, benchmark client, 4000/200 workload, 60/120/30 ranked protocol, short and long checks are unchanged. Both have separate post-score N48 profiles. The change affects all NCCL collectives within prefill, so it is not an all-reduce-only causal intervention.

[The hypothesis and activation requirements](PLAN.md) follow the completed scoped trial, which had no named Simple all-reduce in its separate trace. No new runtime activation or performance gain is claimed by these receipts. Actual kernel/communicator evidence, full local gates and independent repeat of any useful gain remain necessary. Official accuracy remains unverified.

Published ledger at 19/10/2026-22:20:02 SGT: Used 30729.102 SU, Balance 33270.898, In Doubt 0.000. New maximum reserve 3072 SU, total with attention 4608 SU. Internal remaining headroom 15662.898 SU under unchanged 51000-SU cap and 13000-SU buffer. Maximum reservation is not actual expenditure; account for any ledger lag without subtracting prepayment twice. At most three active PBS jobs and one running 16-GPU allocation.

Evidence: pbs-receipts.json, pbs-pre-submit.txt, pbs-post-submit.txt, pbs-upload.txt and validation.json. No uncertain submission, VPN authentication, scheduler automation, slide or official-package change.
