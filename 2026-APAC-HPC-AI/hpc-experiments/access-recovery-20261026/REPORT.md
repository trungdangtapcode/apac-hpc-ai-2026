# CPU access checkpoint — 26 October 2026

The HPC thread restored a separate CPU SSH connection using the existing user-authorized credential through the existing VPN namespace. A new CPU-only multiplexed master was verified with actual hostname asp2a-login-nscc02. The helper now selects cpu-r6; older private state was preserved. No VPN logout or restart was performed, and no credentials or authentication state are included here. This does not establish remaining VPN lifetime.

The CPU queue was empty in the retained query. The site report displayed 27,532.791 SU balance, 2,467.209 SU used, and zero in doubt, as of 25 October 21:55:31 site time; this is a potentially lagging report, not individual job billing.

Installed mpirun resolves to the same PALS 1.1.6 mpiexec executable. Merely renaming mpiexec to mpirun is not a new implementation hypothesis. A controlled test of global versus command-specific binding syntax and a bare launcher is being prepared.

Iris also remains reachable through an interactive gateway auto-jump. One initial bridge connection failed before the Iris prompt; a fresh interactive connection and later bridge attempts succeeded. This is not evidence that Iris scheduler access is unavailable.
