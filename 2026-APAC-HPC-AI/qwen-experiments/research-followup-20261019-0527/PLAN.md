# Bounded load followup after complete source review

The source measurements and exact new IDs are in [RESULTS.md](RESULTS.md). H200 N60 passed at 2839.532 good tokens/s and H100 N54 at 2430.891; neither new load has an independent repeat yet.

Submit one repeat plus one further load step on each platform: H200 N60 repeat then N62, H100 N54 repeat then N56 in a serial PBS chain. Retain all serving/runtime/client/quality payloads unchanged and freeze new metadata hashes. Use each same-platform repeat as the fresh control. Prior H200 chunk/backend jobs keep queue positions. Require all terminal raw protocol/runtime/output gates and preserve failure evidence. No unchanged retry or automatic higher load follows this batch.

The maximum new PBS reservation is 3072 SU under the existing operating budget. Reconcile only terminal charges already reflected in Used; retain any ledger-lag maximum reserve. No new budget, model precision, GPU count, official accuracy claim or background scheduling is authorised by this plan.
