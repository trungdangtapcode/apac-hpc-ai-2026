# ASPIRE-2A CPU access is now authenticated

At 2026-10-21T13:40 UTC a normal interactive password SSH login succeeds on
asp2a-login-nscc02 through the existing VPN. No VPN reconnect or new DUO
request is needed. The prior password-free batch denial below is historical;
it never tested the supplied password. The newly authenticated CPU connection
also passes a subsequent password-free command through its separate SSH master.
No credential or session bytes are retained in research.

The CPU account is apacsc42, project **59000042**, titled APAC HPC-AI Competition
2026 2A 42. The project's displayed ledger is dated 21 October 16:57:58 site
time: Grant 30000 SU, Used 222.154 SU, Balance 29777.846 SU, In Doubt 0 SU.
This is a dated server report, not instantaneous accounting. Its reported CPU
rate is 1 SU/core-hour. It is separate from the AI/H100 project 59010042.
The own CPU queue is empty; normal routes to CPU and GPU queues, the official
openfoam/2512 module exists, and the official shared mesh archive is readable.
No CPU qsub acceptance or result is claimed solely from login/module visibility.

Scratch quota reports 100 TB and 200 million inodes, usage about 17.01 GB;
home about 2.63 GB of 50 GB. Existing CPU research from October 9–10 is found
under scratch/apac2026/hpc. Preserve and inspect it before new spending; it
contains failed/incomplete work and is not automatically a valid Basic baseline.
A collector initially used Python's capture_output argument on the site's
Python 3.6 and stopped. Replacing it with PIPE/universal_newlines succeeds;
this collector error did not execute or fail a solver.

The reusable helper is tools/nscc-cpu-ssh.sh. Its CPU address workaround uses
the original host-key alias and the existing private operational known-hosts
file. Its connection state remains outside the archive. The DNS issue in the
current VPN namespace and all earlier probes are retained below for provenance.

---

## Historical pre-authentication investigation

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
