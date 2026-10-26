# CPU access checkpoint — 26 October 2026

The HPC thread restored a separate CPU SSH connection using the existing user-authorized credential through the existing VPN namespace. A new CPU-only multiplexed master was verified with actual hostname asp2a-login-nscc02. The helper now selects cpu-r6; older private state was preserved. No VPN logout or restart was performed, and no credentials or authentication state are included here. This does not establish remaining VPN lifetime.

The CPU queue was empty in the retained query. The site report displayed 27,532.791 SU balance, 2,467.209 SU used, and zero in doubt, as of 25 October 21:55:31 site time; this is a potentially lagging report, not individual job billing.

Installed mpirun resolves to the same PALS 1.1.6 mpiexec executable. Merely renaming mpiexec to mpirun is not a new implementation hypothesis. A controlled test of global versus command-specific binding syntax and a bare launcher is being prepared.

Iris also remains reachable through an interactive gateway auto-jump. One initial bridge connection failed before the Iris prompt; a fresh interactive connection and later bridge attempts succeeded. This is not evidence that Iris scheduler access is unavailable.

## Later correction at 08:08 UTC

The 06:11 UTC IKE expiry is now verified in the private client log, approximately 24 hours after establishment. A later authorized reconnect returned Authentication failed. Do not attribute this response specifically to DUO, an incorrect password, or server policy without evidence. Existing private state was preserved. The NSCC diagnostic deployment failed before namespace routing and no qsub was called; its budget has not changed. Iris jobs use separate SSH access and remain available.

The first read-only GPU SSH master attempt authenticated but could not create its Unix socket because the path was too long. A shorter separate path succeeded, and a login-shell qstat found no own PBS jobs at that dated observation. The socket creation failure must not be described as an authentication rejection. No AI payload or job was changed. Those connections predate the later VPN expiry and are not current access evidence.

## Access restored again later in this turn

A later read-only check found an already live VPN namespace and a live VPN terminal. The reconnect helper's dead-pane guard refused to respawn it, preserving the active session. A fresh separate CPU master, cpu-r8, then authenticated and returned asp2a-login-nscc02. The standard read-only GPU helper returned a2ap-login01 and an empty own PBS queue. The CPU helper now selects cpu-r8. These are later verified observations; the earlier rejection remains historical. No active VPN was restarted and no AI job or payload was changed.

This enabled the locked admission of CPU diagnostic 25999546.pbs101. Its exact receipt and budget are under nscc-cpu-launcher-order-20261026; no submitted diagnostic payload was modified during recovery.
