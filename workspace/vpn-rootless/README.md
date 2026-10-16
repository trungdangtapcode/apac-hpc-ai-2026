# Rootless Check Point VPN on this login node

Installed2026-10-15 without sudo. No Docker daemon is needed.

Installed from the projects' GitHub releases and checked against their release
asset SHA256 digests:

- slirp4netns1.3.6: user-mode Internet connection for the private network namespace.
- snx-rs6.5.1: community Check Point VPN client, using IPsec over TCP (TCPT).

## Verified

- A regular user can create a user/network namespace and a TUN device here.
- The private namespace can connect to the Internet and NSCC gateway TCP443.
- The TLS chain for `vpn1.nscc.sg` verifies against the system roots after adding
  the missing GlobalSign intermediate, fetched over verified HTTPS from its issuer.
- Client info successfully discovers `NSCC_LDAP` / `vpn_CISCOPROXY_LDAP`.
- A second terminal can enter the same namespace.
- IPsec/TCPT login succeeded and the gateway assigned a VPN address.
- TCP22 on `aspire2p.nscc.sg` (`10.103.72.200`) returns an OpenSSH banner through
  the tunnel. Repeated probes succeeded, with traffic received on `snx-tun`.
- The host route remains `default via198.18.151.2 dev eth0`; no host DNS or route
  configuration was changed.

**VPN authentication, data transfer and SSH account login work.** On2026-10-15,
password SSH authentication succeeded and remote `hostname` returned
`a2ap-login02`. No DUO challenge appeared in this tested client flow. This does not establish
that every NSCC login method or future session has the same authentication flow.

The initial SSL attempt stalled during tunnel setup after authentication. IPsec
over UDP obtained an address but received no tunnel data and failed keepalive.
IPsec over TCP works through this rootless network; it is now the default.

## Commands

From this directory, query gateway capabilities without signing in:

```bash
bash vpn.sh info
```

Start the VPN interactively. The client prompts for the password; no password is
included in the script, configuration or command-line arguments:

```bash
bash vpn.sh connect
```

Keep that terminal open. In another terminal, inspect the VPN's network namespace:

```bash
bash vpn.sh enter ip -brief address
bash vpn.sh enter ip route show
bash vpn.sh enter bash --noprofile --norc
```

SSH through the existing VPN from another terminal:

```bash
bash /home/apacsc42/workspace/vpn-rootless/vpn.sh ssh
```

For a quick remote check, append `hostname`. SSH host-key verification and SSH
authentication are separate from the VPN login. The helper uses the recorded
host key and `-F /dev/null`: the host's system SSH include files appear to have
unmapped ownership inside the user namespace, so the normal system configuration
otherwise fails its ownership check. No host SSH configuration was modified.

`enter` joins the existing VPN namespace; `shell` creates a new independent
namespace without a VPN. Processes launched outside the VPN namespace do not
automatically use the tunnel.

The namespace uses its own hosts/resolver files and a private `/run` tmpfs.
`connect` disables automatic DNS changes by the client. `enter` configures the
advertised NSCC DNS servers only inside the private mount namespace. As those
resolvers did not resolve the public login hostname in our test, the wrapper also
adds `vpn1.nscc.sg` and `aspire2p.nscc.sg` to the private hosts file, resolving them
on the host before starting a new namespace (with a public DoH fallback).
The explicit private routes cover the observed DNS/login/gateway IPs; review
them if NSCC changes those endpoints. Inspect policy routes with `ip route show
table all`; the client places VPN routes in table18000, not just the main table.

Ctrl+C in the connect terminal stops the foreground VPN; the wrapper cleans up
its namespace process and slirp helper. It does not disconnect other users or
alter Slurm jobs.

## Source and limitation

[slirp4netns](https://github.com/rootless-containers/slirp4netns),
[snx-rs](https://github.com/ancwrd1/snx-rs),
[NSCC Linux VPN guide](https://help.nscc.sg/wp-content/uploads/ASPIRE2AP-VPN-Linux.pdf).
This community-client setup differs from NSCC's documented browser/CShell setup;
gateway discovery, VPN authentication and SSH account login have worked
in this test. Compute allocation is a separate step.

`inspection/` retains release metadata, public certificates and their provenance.
`run/` contains temporary namespace state. Neither directory is intended to store
passwords or OTPs. The supplied `.org` hostname failed TLS hostname verification;
all authentication attempts use the documented `.sg` gateway with TLS verification.

## IKE lifetime correction2026-10-15
The previous helper inherited snx-rs6.5.1 default28800s(8h). It now explicitly requests86400s(24h) for new IPsec connections. This is separate from SSH ControlPersist. Gateway negotiation and actual24h operation remain unverified; see inspection/ike-lifetime-diagnosis.json.

## Next authorized login: detached terminal and private session cache

Prepared16Oct after the second unexplained drop. Do not authenticate until the
user explicitly authorizes a new attempt and the DUO holder is available.

Use `bash vpn-persistent.sh connect` from this directory; it creates a tmux-owned
PTY and attaches for the password/MFA prompt. Detach with Ctrl-B then D; closing
an attached client does not normally close the tmux-owned PTY. `attach` reconnects
only to that terminal; `status` inspects and does not start a login. A dead pane
is retained for diagnosis. Private INFO/exit logs are under `private-logs/`.

Helper IPsec requests86400s and now enables `ike-persist=true`. `netns.py` binds
`private-cache/` to `/var/cache` ONLY inside the VPN namespace, so the client's
SQLite state can survive namespace teardown. Directories0700/files0600; no
password keychain, no password in script/config or notes. Session state is still
sensitive. Persistence can help restart/drop recovery; it cannot guarantee reuse
of an expired/revoked SA, extend server limits or reuse the Windows session.

This new launcher has NOT authenticated to NSCC yet. Local probes verified PTY
survival after the launcher exits, hidden mock input not appearing in pane logs,
private dummy state surviving a namespace exit and host `/var/cache` unchanged.
They do not establish24h reliability or prove the previous disconnect cause.
See `inspection/persistent-launcher-validation.json` and
`inspection/vpn-drop-forensics-20261016.json`. No new authentication was attempted.
