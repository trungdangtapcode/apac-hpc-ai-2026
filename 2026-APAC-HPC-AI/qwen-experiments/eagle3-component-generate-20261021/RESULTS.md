# Terminal review — 2026-10-21T03:47:36.167470+00:00

**222722 F / exit 1**, 89 seconds / estimated 3.164444 SU. Native /generate synthetic gateway forwarding passes; the following component imports fail at read-only HOME, before native config/tensor checks. [Complete assessment and repair provenance](REVIEW.md). The submission snapshot below is historical.

# Derived component gate submitted — 2026-10-21T03:42:14.595996+00:00

Definite **222722.pbs111**, initial state **R**. One H100 / four minutes / maximum 8.533334 SU. [Receipt](pbs-receipt.json), [scheduler state](post-submit.txt), [exact derived route and limits](PLAN.md). No model result, numerical pass or performance claim yet.

The actual own queue was empty before qsub. Fresh locked ledger: Used 43571.410 / Balance 20428.590 / In Doubt 0.000 SU. The prior failed component's 105-second estimated cost remains unposted, so retain its full maximum plus the new maximum: 17.066667 SU total. Internal headroom is **7411.523333 SU**, unchanged 51000 cap / 13000 buffer. [Structured commands](pre-submit-commands.json), [reconciliation](reconciliation.json).

The actual native gateway's filtered chat extension is preserved in terminal 222721. This is a distinct /generate+logprob diagnostic with a single container invocation; the tensor/config checker is byte-identical. Synthetic response IDs never count as model output. The official AIPerf command and native serving code remain unchanged. After a component PASS, real model loading, exact token coverage, target-only stability, both-phase PD transfer and greedy equivalence still need a separately justified integration test. No blind repeat, automation or submission edit.
