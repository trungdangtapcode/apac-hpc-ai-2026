# Actual unobserved H100 scheduler check submitted

Both frozen payloads passed syntax, source-checksum and inverse-diff validation. Fresh SSH/PBS access and project credit were checked before reservation and submission. The own queue was empty and the published Used matched the reconciled local ledger. Exactly two jobs were reserved/submitted once, with each returned ID persisted immediately; no uncertain submission or retry occurred.

| Job | Trial | State at 06:21:45 UTC |
|---|---|---|
|222178.pbs111|Unobserved interval2 candidate, N54|R|
|222179.pbs111|Fresh unobserved interval1 control, N54|H, afterany 222178|

The actual PBS dependency is verified; at most one 16-GPU allocation runs. Both retain native checkpoint/numerics, chunk4096, both-phase HPC-Ops, FA3 prefill/FlashInfer decode, topology, NIXL, MNNVL, complete streaming 4000/200 and 60/120/30 plus short/12-long checks. Only decode receive interval differs between inference commands. Uniform scored hardware telemetry is intentionally off on both; separate CPU/GPU diagnostic and full raw score/output/runtime checks remain. There is no result yet.

Maximum outstanding reserve is **3072 SU**, internal headroom **11619.806 SU** under unchanged 51000 cap and 13000 project buffer. Pre-submit published Used **36308.194 SU**, Balance **27691.806 SU**, In Doubt zero, with the source's own publication timestamp retained in nscc-budget.json. Maximum reservation is not the expected charge and not an additional debit to subtract twice from published balance/prepayment.

[The plan](PLAN.md) records the small +0.480% observed polling result, −1.550% single on/off difference, exact candidate/control and reversed order, full gates and stopping rules. No optimisation is promoted, official accuracy claimed, interval/load increased, frozen job changed, slide/package modified or background Codex launched. Current VPN/SSH are left running.
