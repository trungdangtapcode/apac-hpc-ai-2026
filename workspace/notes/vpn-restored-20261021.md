# VPN and PBS access restored — 21 October 2026

The owner explicitly requested another login. A read-only check found the
existing tmux VPN pane dead and no live namespace. Only the dead pane was
respawned; private recovery state and prior logs were preserved. The client
requested its password through a terminal with echo disabled. SSH separately
required password authentication because the previous master was absent.
The previously supplied credential authenticated both. No password, OTP,
session database, paste buffer or private log is included in these records.
No phone-side DUO action was observed; successful access does not establish
which MFA factor was used by the gateway.

A fresh batch SSH command returned a2ap-login01 and server UTC
2026-10-21T09:56:56Z. The own PBS queue was empty at that query. Leave the live
VPN process and new SSH multiplexing master running. The client still requests
86400 seconds; negotiated expiry and the old disconnect cause are unverified.

222780.pbs111 is now collected and sealed: F/exit 1 after 1661 seconds,
estimated 944.924444 SU, no request result or score. Decode completes target/
draft graphs and reaches readiness, so the earlier RMSNorm failure no longer
blocks it. Prefill ranks diverge around an automatic local-memory graph gate
and health times out. This is an observed startup failure, not a completed
correctness measurement or a proven NIXL communication defect.

See the [full run review](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/eagle3-pd-bf16-20261021/REVIEW.md).
The next bounded hypothesis disables prefill graphs uniformly, first on one
TP4 prefill. It still needs native source/guard checks, a fresh locked budget,
a frozen probe and a definite receipt. No new GPU spending is implied by this
access record. Existing H200 queue positions and the accepted submission remain.
