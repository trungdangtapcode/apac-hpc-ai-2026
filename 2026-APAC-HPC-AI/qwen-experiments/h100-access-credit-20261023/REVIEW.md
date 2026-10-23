# Existing H100 access works; native probe charge posted

At 2026-10-23T04:09:59.305523+00:00, an existing authenticated SSH master successfully executes the login environment on **a2ap-login01**. The selected AI project 59010042 queue is empty. No VPN/client was restarted, no new password or DUO authentication was attempted, and no CPU-project queue or ledger was queried. This does not establish when another session restored access, which factor authenticated it, or the VPN lifetime.

The first remote Python command omitted `bash -lc`, so `qselect` was absent from PATH even though SSH worked. The next login-shell command found older 222407/222408 PBS history purged; that is not an authentication failure. The successful snapshot requests only still-retained 223132 and selected AI project records. [Safe current command/accounting evidence](access-and-accounting.json), [first PATH failure](initial-nonlogin-command.stderr). The repeatable check accepts an already-existing socket path as an argument; no live socket, authentication cache, credential or concrete session identifier is captured.

## Fresh selected AI credit

Published balance as of **23/10/2026-12:00:01** (server display): grant 64000.000 SU, used 46404.261 SU, balance 17595.739 SU and In Doubt 0.000 SU. Retain server display and local observation timestamps separately.

Fresh job 223132 is terminal F/0, allocated two GPUs for 315 seconds: 22.4 SU at 128 SU/GPU-hour. The published Used increment is exactly 22.4 SU to displayed precision, uniquely explaining the only unposted owned charge. Under the budget lock, mark that job posted and release only its 42.666667 SU maximum reservation. No other job/cost was inferred or released. [Reconciliation](RECONCILIATION.json).

The unchanged 51000 SU operating cap and 13000 SU project reserve leave **4595.739 SU** internal headroom, with zero outstanding maxima after reconciliation. Public balance already reflects in-doubt prepayment; never subtract it twice. No new reservation or GPU job was created by this access/accounting review. Any next experiment needs a justified hypothesis, fresh locked queue/credit checks and a separate definite receipt; the CPU project's budget is independent.
