# H100 existing-access check — 26 October 2026

Observed 2026-10-26T08:30:38.017677+00:00. The persistent VPN helper reports its pane dead with exit status 1; no running snx-rs process is found. The documented BatchMode SSH helper exits 1 because it cannot find a live VPN session, before running the remote hostname/date command. This is an unavailable VPN path. It is not a measured SSH password rejection, a PBS outage or evidence of a gateway MFA rejection in this check.

No VPN restart, fresh gateway login, password input, DUO push, remote scheduler query, SU query or GPU submission was performed. Prior private recovery/session files were left untouched and not captured. The reason/time of disconnect and negotiated lifetime remain unknown. A Windows VPN connection is independent and does not prove this machine still has a tunnel.

The user calls this the DUO server: DUO is the phone-based MFA stage for access, while the AI compute service is the separate H100/PBS cluster. The path is local VPN → SSH authentication to H100 login → PBS queue/credit. A failure at the first stage prevents observing the later ones; do not call queue empty or show a dated budget as live.

Current H100/PBS queue and balance are UNKNOWN. Retained last budget snapshot (24 October site label 21:20:08) is used 46937.772 SU/balance 17062.228 SU/In Doubt 0, not current credit. H100 best retained full N54 individual remains 2433.019859 good output tokens/s (222048), separate from H200 and not a fresh score.

A status-only request does not initiate new MFA; the persistent access policy explicitly preserves authentication state and requires current authorization for a fresh login. Existing H200 research continues independently: five jobs 26315/26317/26319/26337/26347 remain pending at the 08:29 UTC scheduler query. No HPC worker payload, queue or CPU-project ledger was changed.

[Sanitized observation](OBSERVATION.json). Only boolean/result classifications are retained; no password, session identifier, socket path, auth cache or raw gateway log is saved here.
