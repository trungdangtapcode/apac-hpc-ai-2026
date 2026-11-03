# Try one VPN login

On the current research machine, run:

```bash
python3 /home/apacsc42/workspace/submission-tools/vpn-login-once.py
```

Each explicit invocation starts at most one authentication attempt. It preserves an existing pending login or reachable VPN transport and refuses concurrent launcher invocations. It does not schedule retries. Approve DUO on the authorised phone if a notification arrives; gateway rejection does not establish whether DUO was delivered.

The launcher uses the existing private local credential helper in `run/credential-reconnect.local.py`. That helper, authentication caches, session state and private logs must stay outside Git. `APAC_VPN_CREDENTIAL_HELPER` may select another locally provisioned helper; it must accept no arguments, supply credentials privately and never print secrets. A fresh checkout alone does not restore authentication. If the helper is missing, use `bash vpn.sh connect` and type the password interactively. The existing local helper requires the retained local recovery source and a dead `nscc-vpn` tmux pane; a missing helper prerequisite stops the attempt without exposing its output.

Successful output indicating SSH transport reachability is not authenticated SSH access. To check the CPU login after VPN connects:

```bash
bash /home/apacsc42/workspace/vpn-rootless/vpn.sh ssh-batch "hostname"
```

Sanitised per-invocation receipts are written under `inspection/manual-login-attempts/`. No password, OTP, private client output or session object is recorded there. Do not run the launcher while a separate interactive `vpn.sh connect` login is pending. The local credential helper is a preserved machine-specific prerequisite, not part of the reproducible public source.

## How long can the captain take to approve?

The server-side DUO approval deadline has not been established. Two retained 3 November attempts returned gateway Authentication failed after approximately 4.52 and 4.50 seconds. That does not establish that DUO arrived or that the captain missed its deadline.

The launcher polls up to 12 times with a 3-second pause (about 36 seconds plus transport-check overhead). If authentication is still pending, it leaves the VPN client alive; that observation window is not a DUO timeout. Its 45-second helper timeout concerns local credential handoff, not the phone approval deadline. Extending local polling cannot prevent a gateway rejection.
