# User-authorised H100 capacity and backend interaction — 17 October 2026

User requested reauthentication and additional submissions; SSH password login
succeeded through unchanged VPN without new DUO. Existing pair is terminal exit0;
ledger delta2541.796SU reconciles walltimes, used8204.517SU, balance55795.483SU.

220909 repeats MNNVL N42 at2041.093goodtok/s,SLA99.055% versus2207202041.966.
N32/N34 vs fresh220908:1680.796/1758.237 versus1563.237/1624.351.
Full sealed raw/protocol/short/long/runtime review must pass before newqsub.
Task-side logging now contains MNNVL initialization ranks0..7/world8; old missing
logs are resolved for this repeat, not retroactively for earlier jobs.

Amend prior no-N44 plan based on this new evidence and explicit current request:
09 MNNVL capacity: planned42,44,46,48, stop on first failed SLA/error gate.
10 MNNVL+FlashInfer interaction: same planned loads/stop rule, add only decode
attention backend FlashInfer. Standalone FlashInfer loss onH100 does not predict
its interaction with MNNVL; positiveH200 interaction motivates measuring here,
not assuming transfer. N42 anchor uses repeated MNNVL capacity controls; higher
loads compared only if both new trials measured the sameN.

Each16H100/45min; strict09→afterany10, max1running16GPU and cap3queued/running.
Reserve3072SU under budget.lock before qsub, fresh full ownqueue+myprojects,
campaigncap16384SU and projectretain13000SU. Postreserveheadroom5107.483SU
if no other charges. No new dataset/precision/model/topology; same logging,
protocol60/120/30,4000/200,RR/NIXL and postmeasure short+12longdiagnostics.
No automatic repeat or promotion; errors, quality failures or deferred long
checks remain evidence. Organiser99%accuracy remains unverified.
