# Can the DUO-connected server run the HPC task?

Checked on 21 October 2026. DUO authenticates the VPN connection; it does not
select a compute cluster or grant a CPU project. The existing authenticated
SSH session reaches a2ap-login01 on ASPIRE-2A+ (aspire2p.nscc.sg), the AI/H100
system. Its live normal routing queue has route_destinations = aiq1,aiq2.
The CPU OpenFOAM module is not listed by the bounded module query and the
published ASPIRE-2A CPU shared mesh path is not readable there. These are
observations of this login, not proof that CPU code cannot run on GPU hosts.

The contest HPC result requires four standard CPU nodes on ASPIRE-2A (AMD
EPYC 7713), or Gadi normalsr. Running CPU code on the H100 hosts does not
turn that allocation into the specified contest CPU hardware. No speculative
CPU job is submitted to the AI queue merely to test its submission filters.

ASPIRE-2A has a separate SSH endpoint: aspire2a.nscc.sg (login.asp2a.nscc.sg
is an official alternate). The live AI login resolves it to 10.103.72.110.
The current VPN namespace can reach this IP and complete the SSH handshake.
An initial hostname probe failed at DNS; using the resolved IP with the correct
HostKeyAlias reaches the SSH server. A probe from the AI login itself times
out, which does not negate the working VPN-client route.

The new endpoint initially has no retained host key; normal first-contact
accept-new stores that public host key only in the private operational known
hosts file outside research. A subsequent password-free BatchMode probe returns
Permission denied (publickey,gssapi-keyex,gssapi-with-mic,password). This means
there is no reusable noninteractive authentication for this separate SSH
server in that probe. It does not prove that the user's password is wrong,
that the CPU account is disabled, or that VPN/DUO failed. No password or OTP
was submitted, no new DUO request was triggered and the existing VPN/AI SSH
session was preserved. Do not record authentication material in this report.

Next establish an interactive CPU SSH login, inspect myprojects, queue access,
the native openfoam/2512 module and CPU charging there before any qsub.
The AI login's project 59010042 is explicitly titled Competition 2026 2A+ 42;
that title and its CPU Hour accounting row alone do not verify CPU-cluster
project eligibility. The refreshed AI ledger is retained only as a dated
read-only observation, not reconciled into another worker's budget files.
No CPU/GPU reservation or job was made by these access probes.

Sources:

- [Official task hardware and cluster rules](https://github.com/hpcac/2026-APAC-HPC-AI/blob/main/2.%20OpenFOAM%20HPC%20Task%20Rules.md)
- [Official ASPIRE-2A OpenFOAM application notes](https://github.com/hpcac/2026-APAC-HPC-AI/blob/main/4.3%20OpenFOAM%20Application%20Notes%20-%20ASPIRE-2A.md)
- [NSCC ASPIRE-2A access](https://nsccsg.github.io/systems/aspire2a/access/)
- [NSCC ASPIRE-2A FAQ: endpoint and CPU charging](https://help.nscc.sg/aspire2a/faqs/)

Exact safe probe responses are the three adjacent JSON files. The earlier
non-login-shell query lacked qstat/myprojects in PATH; bash -lc resolves that
shell-environment issue. Missing PATH commands were not a scheduler outage.
