# 23 October: existing AI SSH path is usable

A read-only check uses the already authenticated AI SSH master and reaches `a2ap-login01` with the cluster login environment loaded. The selected AI project 59010042 queue is empty, and project credit is fresh. No VPN restart, password, DUO action or replacement session was requested. The cause and time of access restoration and actual negotiated lifetime were not established by this check.

The 22 October failed-authentication record is historical, not a live claim that access remains unavailable. The first command today lacked the remote login environment and could not find qselect; SSH itself had succeeded. An older pair of job IDs is no longer retained by PBS; the still-retained 223132 is sufficient to reconcile its uniquely matching posted charge. Do not label command/PATH/history errors as VPN or SSH authentication failures.

[Current access, accounting and limitations](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-access-credit-20261023/REVIEW.md). No authentication material or live connection state is retained here.

## Current read-only recheck — 23 October, 12:37 UTC

The existing authenticated AI SSH master answers its local control check, and an actual remote command reaches `a2ap-login01` successfully. The selected AI project 59010042 query also returns successfully with no queued/running AI PBS job. This establishes that the existing SSH path is usable at this observation, not merely that a local process exists. No new VPN login, DUO push, password input, restart or replacement session was attempted. Fresh DUO authentication therefore remains untested.

DUO is an authentication step, while an SSH master is an already authenticated connection that can open another command channel. Reusing that connection does not perform a new login. A working old channel does not establish whether a new DUO push would arrive or be accepted, nor does it prove a requested 24-hour VPN lifetime was negotiated or that every new connection would work. Preserve those distinctions when troubleshooting.

## Submission confirms the existing path — 13:08 UTC

The same authenticated path successfully uploaded a frozen AI diagnostic, queried the selected AI queue and project credit, submitted 224116.pbs111, and read its running scheduler record. No VPN restart or new DUO authentication was attempted. This confirms usable current research access; fresh DUO push delivery and acceptance remain untested.

## Later loss of access — 2026-10-23T14:29:18.814708+00:00

The original working connection snapshot is historical. Before a new diagnostic submission, the local AI SSH master check fails. A read-only persistent-helper status shows a dead VPN pane; entering the expected namespace reports no live VPN session. These establish that no current usable VPN namespace is present, not why it stopped. Do not infer expiry, a gateway authentication rejection or a client bug from the missing master alone. No restart, credential input or DUO step was attempted. Phone-holder availability for a fresh authentication was asked. Private recovery state is preserved. The intended diagnostic was not uploaded, reserved or submitted.

## VPN restored; AI SSH still needs authentication — 2026-10-23T15:09:49.749526+00:00

A fresh read-only status check finds a live persistent VPN pane and tunnel interface. The AI SSH helper reaches the expected H100 SSH host through that namespace with host-key verification, then exits with `Permission denied (password)` in BatchMode. No password was supplied in this check, so this is not evidence that the owner's password was rejected. It establishes working reachability to the SSH authentication stage, while the old AI SSH master is absent and a new authenticated H100 channel has not been established.

The separate HPC handoff records that its worker restored the shared VPN. This AI session did not perform that login or observe phone-side DUO approval. Do not restart the healthy shared VPN or infer that successful CPU SSH is an authenticated H100 SSH session: they use different login hosts. The earlier unavailable-VPN observation is historical. The earlier question about DUO-holder availability no longer blocks reuse of the now healthy VPN. Preserve all private recovery state; no authentication material is retained here. No queue, credit or submission was changed by this check.

For troubleshooting: a VPN supplies a network path; SSH then authenticates to a particular server. A BatchMode password prompt failure can occur simply because no reusable SSH channel or noninteractive credential is available. It does not establish gateway MFA failure or an expired VPN.

## AI SSH authenticated again — 2026-10-23T15:28:36.236392+00:00

The AI worker reused the healthy shared VPN and authenticated SSH to the expected H100 server using the previously supplied credential through a terminal with echo disabled. A remote command returns a2ap-login01. No VPN restart, fresh gateway authentication or phone-side DUO step was performed by this worker. No credential was written into scripts, research artifacts or notes. The SSH service reports that the account password will expire in three days; this was a server notice, not a VPN lifetime. No password change was attempted.

The selected AI queue 59010042 is empty, and fresh selected credit successfully reconciles the uniquely posted 224116 charge 16.284 SU. Existing CPU-project access/queues/budget are untouched. The earlier unauthenticated AI SSH snapshot is historical.
