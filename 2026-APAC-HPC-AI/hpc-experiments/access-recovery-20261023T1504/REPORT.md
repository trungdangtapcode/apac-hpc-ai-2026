# VPN and CPU access recovery — 23 October 2026

The previous VPN terminal was already dead when checked at 14:49 UTC. An explicitly authorized restoration at 14:55 ended with gateway `IPsec authentication failed, status: 0` and `Authentication failed` at 14:56:20. The cause was not established: neither an incorrect password, missing phone approval nor a server lifetime was proved. No private cache was deleted.

The owner explicitly authorized another DUO attempt. A new attempt started at 15:04:30 and the VPN reported connected at 15:04:45 UTC. Phone-side approval was not observed by this worker; a successful tunnel does not establish its future lifetime. The tmux-owned terminal was detached without stopping the VPN. The old private caches and logs were retained outside the archive. The dead pane's old log pipe was closed before opening a fresh private log.

The old CPU multiplexing path could not authenticate a fresh batch request. A separately authenticated cpu-r3 master successfully reached asp2a-login-nscc02; the helper now selects it. Old CPU and AI masters were not killed. A functional read-only hostname/PBS query succeeded. Credentials, raw login banners, cached session state and socket files are excluded from this report and Git. No credential rotation was performed.

The whitelisted scheduler snapshot confirms job **25940700.pbs101 remains Q in q5**, with `Not Running: Insufficient amount of resource: node_pool`. This is a fresh dated queue observation, not a performance result. No qsub, cancellation, budget increase, reservation retirement or AI queue change occurred. Preserve this independent confirmation and its queue position.

The terminal also displayed inconsistent password-expiry warnings (three and four days); these are not a measured session timeout and no password was changed.
