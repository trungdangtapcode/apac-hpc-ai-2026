# 23 October: existing AI SSH path is usable

A read-only check uses the already authenticated AI SSH master and reaches `a2ap-login01` with the cluster login environment loaded. The selected AI project 59010042 queue is empty, and project credit is fresh. No VPN restart, password, DUO action or replacement session was requested. The cause and time of access restoration and actual negotiated lifetime were not established by this check.

The 22 October failed-authentication record is historical, not a live claim that access remains unavailable. The first command today lacked the remote login environment and could not find qselect; SSH itself had succeeded. An older pair of job IDs is no longer retained by PBS; the still-retained 223132 is sufficient to reconcile its uniquely matching posted charge. Do not label command/PATH/history errors as VPN or SSH authentication failures.

[Current access, accounting and limitations](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/h100-access-credit-20261023/REVIEW.md). No authentication material or live connection state is retained here.

## Current read-only recheck — 23 October, 12:37 UTC

The existing authenticated AI SSH master answers its local control check, and an actual remote command reaches `a2ap-login01` successfully. The selected AI project 59010042 query also returns successfully with no queued/running AI PBS job. This establishes that the existing SSH path is usable at this observation, not merely that a local process exists. No new VPN login, DUO push, password input, restart or replacement session was attempted. Fresh DUO authentication therefore remains untested.

DUO is an authentication step, while an SSH master is an already authenticated connection that can open another command channel. Reusing that connection does not perform a new login. A working old channel does not establish whether a new DUO push would arrive or be accepted, nor does it prove a requested 24-hour VPN lifetime was negotiated or that every new connection would work. Preserve those distinctions when troubleshooting.

## Submission confirms the existing path — 13:08 UTC

The same authenticated path successfully uploaded a frozen AI diagnostic, queried the selected AI queue and project credit, submitted 224116.pbs111, and read its running scheduler record. No VPN restart or new DUO authentication was attempted. This confirms usable current research access; fresh DUO push delivery and acceptance remain untested.
