> Historical 22 October authentication failure. On 23 October a read-only check reused an existing authenticated AI SSH connection successfully; no login or VPN restart was performed. See [current access evidence](vpn-access-20261023.md).

# VPN authentication attempt — 22 October 2026

Recorded 2026-10-22T14:15:37.078526+00:00. The owner explicitly asked to retry VPN login and DUO if authentication was required. The read-only check found the old tmux pane dead with exit status 0 and no live VPN namespace. This is not evidence of its disconnect cause or exact negotiated lifetime. The launcher still requests 86400 seconds; that setting does not guarantee a 24-hour accepted session.

Only the dead VPN pane was respawned; private recovery state and old logs were preserved. The previously authorised credential was supplied to a verified password prompt with terminal echo disabled, through a temporary memory buffer deleted immediately after input. No password, OTP, private session cache or raw authentication log belongs in this note or archive.

The gateway returned **Authentication failed** and the new pane then exited. No successful VPN connection was established. A batch SSH check timed out, consistent with the unavailable VPN path; it does not establish a separate SSH password rejection. No DUO push or approval was observed from the client. The exact rejection reason is unknown: do not label the password incorrect or claim MFA was sent/approved without evidence. The owner confirmed that the phone received no DUO notification. This does not identify whether rejection was first-factor validation, an account policy or another gateway condition. No repeated login loop was started.

This access attempt creates no GPU spending, new PBS reservation or HPC CPU access. Existing H200 Slurm work continues independently. The last retained AI PBS budget is dated and has not been refreshed while VPN access is unavailable. Do not present it as live credit. Preserve private recovery state and require concrete new authentication information before diagnosing the failure more narrowly.

## Read-only gateway method check

At 2026-10-22T14:20:02.625646+00:00, public gateway info succeeds without a new login. The gateway still advertises `vpn_Username_Password` and the NSCC_LDAP option `vpn_CISCOPROXY_LDAP`; the current launcher uses the latter, as in the previously working configuration. No certificate/timeout error occurred in this info query. This rules out an absent advertised login method in this check; it does not validate credentials, account/MFA policy or establish VPN access. No second authentication attempt was made.
