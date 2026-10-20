# VPN session duration and how to change the requested lifetime

Checked on 20 October 2026 at approximately 01:04 UTC. This is a read-only inspection of the existing connection; no restart, new authentication or lifetime change was performed.

## What is configured now?

The installed community client is snx-rs 6.5.1, using IPsec over TCP. The active launcher [vpn.sh](../vpn-rootless/vpn.sh) explicitly passes:

```bash
--ike-lifetime 86400 --ike-persist true
```

`86400` seconds is 24 hours. The old default was `28800` seconds, or 8 hours. This value is the requested lifetime of the IKE security association, the negotiated security context protecting the VPN. It is not proof that every gateway accepts exactly that duration or that every login lasts that long.

At inspection the snx-rs process started on **19 October at 04:00:57 UTC** and had been running for **21 hours 3 minutes**. The detached tmux pane was alive and a fresh remote SSH command returned successfully at **20 October 01:04:10 UTC**. Process uptime is not an exact authentication timestamp or proof that no intermediate traffic interruption occurred. The private INFO log did not yield a negotiated IKE lifetime through the narrow safe event extractor, so no exact expiry time is claimed. No session database, key, token or raw private log is included here.

## Why is the connection lasting longer now?

Three separate changes exist:

| Mechanism | Purpose | What it does not establish |
|---|---|---|
| `--ike-lifetime 86400` | Request 24 hours instead of the former 8-hour client default | Guaranteed gateway acceptance or exact expiry time |
| Detached tmux terminal | Keep the client process independent of the calling terminal | An increased authentication lifetime |
| `--ike-persist true` and a private state directory | Let the client attempt recovery using retained IKE state | Unlimited renewal, recovery after revocation/expiry or reuse of a Windows session |

The longer requested lifetime addresses the earlier default. tmux addresses terminal/process lifetime; persistence addresses recovery. Their existence does not prove the cause of every earlier drop. One old disconnect was explicitly logged as `IKE SA expired`; another lacked enough exit evidence for that conclusion. The Linux and Windows clients have independent sessions.

The helper also uses SSH `ControlPersist=86400`. That setting keeps an SSH multiplexing master available after its clients exit. It does **not** set VPN lifetime, renew IKE or extend DUO authentication.

## How can the requested duration be changed?

Edit only the IPsec `--ike-lifetime` argument in [vpn.sh](../vpn-rootless/vpn.sh), then use that configuration on a future authorised connection:

| Desired proposal | Seconds |
|---|---:|
| 8 hours | 28800 |
| 24 hours — current | 86400 |
| 48 hours — example, not tested here | 172800 |
| 7 days — example, not tested here | 604800 |

For example, a future 48-hour proposal would replace the option with `--ike-lifetime 172800`. Editing the file does not update the running process or extend an existing negotiated association. The gateway may choose or enforce a shorter lifetime, revoke access, or require fresh authentication. Do not restart the healthy current connection just to test a longer duration without the user's instruction and an appropriate authentication opportunity. No 48-hour or 7-day connection has been tested here.

In the pinned IKEv1 implementation, the client proposes the configured duration, records the negotiated lifetime, and disconnects when that IKE context expires. Refreshing ESP traffic keys and the assigned-IP lease are separate operations and do not imply indefinite IKE renewal. Therefore, a healthy connection at 21 hours should not be described as automatically renewing beyond 24 hours.

## Safe read-only checks

```bash
bash /home/apacsc42/workspace/vpn-rootless/vpn-persistent.sh status
ps -C snx-rs -o pid=,lstart=,etime=
bash /home/apacsc42/workspace/vpn-rootless/vpn.sh ssh-batch "bash -lc 'date -u +%FT%TZ'"
```

A tmux pane or tunnel interface alone is insufficient proof of end-to-end access; the final command checks SSH through the existing VPN. The `bash -lc` wrapper ensures the remote cluster login environment is loaded. None of these commands starts a new VPN login.

## Primary sources

- [snx-rs 6.5.1 configuration options](https://github.com/ancwrd1/snx-rs/blob/v6.5.1/docs/options.md): lifetime default and session persistence.
- [Pinned IKEv1 implementation](https://github.com/ancwrd1/snx-rs/blob/v6.5.1/crates/snxcore/src/tunnel/ipsec/ikev1.rs): configured proposal, negotiated lifetime, expiry check, separate ESP and address refresh.
- [Earlier retained diagnosis](../vpn-rootless/inspection/ike-lifetime-diagnosis.json): the old 8-hour default and the request change, with its original dated limitations.

Earlier statements that the new launcher had not yet authenticated or that only SSH persistence was changed are historical snapshots. They must not override the inspected current helper or subsequent successful logins. This inspection does not change earlier research queues, scores or credit snapshots.
