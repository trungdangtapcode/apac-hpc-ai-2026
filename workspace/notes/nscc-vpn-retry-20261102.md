# Owner-requested VPN login retry — 2 November 2026

The owner asked to try VPN login again. A read-only check at **10:58:34 Vietnam (UTC+7)** found no usable VPN namespace. A bounded helper preserved the private recovery cache and old logs, restarted only the dead client pane and supplied the already authorized credential through a verified echo-disabled prompt. Exactly **one attempt** ran; no repeated MFA loop was created.

The gateway returned **Authentication failed** at **10:59:50 Vietnam**. The client pane then exited with status 1. A fresh transport probe at **11:00:37 Vietnam** again returned **NAMESPACE_UNAVAILABLE**. No usable VPN or authenticated NSCC access was established, and no SSH authentication was attempted. This is a **VPN gateway authentication failure**, not a tested CPU SSH rejection.

The client evidence does not establish whether a DUO notification reached the captain's phone, whether it was approved, or the exact gateway rejection cause. Do not label the password wrong, the account expired or the session lifetime exhausted without evidence. No lifetime setting, password, private cache, TLS validation or SSH configuration was changed. No private authentication/session material or raw private log belongs in the retained records. The existing private cache and previous logs remain intact.

The reused wrapper's authorization string cites an old 28 October request; that is an inherited template label, not the authority date of this attempt. The **current owner message on 2 November** authorizes it. Its ambiguous private_material_retained=false field refers to the sanitized result, not deletion of recovery state. The derived result clarifies both points and hash-binds the original safe wrapper output.

This attempt creates no CPU/GPU allocation, NSCC reservation or scheduler receipt. The most recent Iris job 2294643 snapshot remains separately dated; this VPN failure does not stop that accepted Iris allocation. No AI payload, queue or handoff was modified. No background Codex or automatic reauthentication loop was started.

[Sanitized result and evidence provenance](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-vpn-retry-20261102/RESULT.json). Reuse a healthy future connection rather than restart it; another failed attempt is not evidence to spam DUO.


## New explicitly requested attempt — 21:06 Vietnam

The owner again asked to try VPN. Precheck at **21:05:37 Vietnam** found namespace unavailable and a dead client pane. Exactly one attempt began at **21:06:42** and returned gateway **Authentication failed at 21:06:46**, followed by namespace unavailable at **21:08:07**. No SSH authentication was attempted. No phone-side DUO delivery/approval or exact gateway rejection cause was observed. Recovery cache and private logs remain intact; no repeated retry loop, configuration change or new spending.

The current request, rather than the reused wrapper's old 28 October label, authorizes this new attempt. The raw safe wrapper output is hash-bound in [the 21:06 result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-vpn-retry-20261102/RESULT-2106.json). No credential, OTP, private client log or session object is retained in the research archive.


## Further explicitly requested retry — 22:06 Vietnam

At the owner's new explicit request, precheck at **22:05:59 Vietnam** found no usable namespace and a dead client pane. Exactly one retry began at **22:06:18**, and the gateway returned **Authentication failed at 22:06:23**. The **22:06:41** transport probe remained NAMESPACE_UNAVAILABLE. No SSH login was attempted. The exact rejection cause and DUO phone delivery/approval remain unknown; no additional attempt was made. Existing private cache and logs were preserved, and no authentication/session material is retained in the archive.

This was a VPN-only action: no scheduler, job, budget or other-track payload changed. The last Iris scheduler snapshot is historical and was not refreshed. [Sanitized result](/home/apacsc42/2026-APAC-HPC-AI/hpc-experiments/nscc-vpn-retry-20261102/RESULT-2206.json).
