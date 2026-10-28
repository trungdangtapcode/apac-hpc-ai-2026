# VPN retry and health-check correction — 28 October 2026

## Actual outcome

The owner explicitly requested another attempt. At approximately 16:36 Vietnam time (UTC+7), a temporary retry wrapper briefly declared a live VPN because `vpn.sh enter true` succeeded. That command proves only that the namespace exists. The namespace is created before VPN authentication, so this was insufficient evidence. The immediate CPU SSH reuse failed with no live session; the client terminal subsequently showed Authentication failed and a dead pane. The public success claim was corrected immediately. The original retry record retains both the historical outcome and its correction; no actual authenticated NSCC access or new job was established.

Two subsequent bounded, authorized attempts used a stronger check and both returned Authentication failed. No indefinite retry loop remains. Private cache/session state was preserved, and research records retain only outcome classifications. No password reset, cache deletion or TLS-verification change was made.

## Correct transport test

`hpc-experiments/tools/nscc_vpn_path_check.py` requires an up `snx-tun` interface with IPv4, then a reachable NSCC CPU TCP22 service returning an SSH banner. It does not authenticate. Its states deliberately separate namespace unavailable, tunnel not ready, tunnel present but SSH unreachable, and SSH service reachable with authentication untested. Only a subsequent successful host-key-verified SSH command can establish usable authenticated CPU access. Merely seeing a namespace or banner must never be called successful login.

Six offline regression tests cover namespace-only startup, absent tunnel IPv4, unreachable SSH, a non-SSH banner, a real-looking SSH banner without authentication, and private stderr exclusion. All pass. The actual current probe returns namespace unavailable.

## Source review and limits

The pinned [snx-rs 6.5.1 IKEv1 implementation](https://github.com/ancwrd1/snx-rs/blob/v6.5.1/crates/snxcore/src/tunnel/ipsec/ikev1.rs) contains a generic authentication-failure path after a status response, and a distinct pending-challenge state. That source does not establish which path this running attempt used, whether a DUO push reached the phone, or whether the current credential expired. The allowlisted terminal classification found only the generic failure, without a captured numeric IPsec status or challenge debug marker. An absent debug marker at info level is not evidence that no challenge occurred.

The [logging documentation](https://github.com/ancwrd1/snx-rs/blob/v6.5.1/docs/options.md) states that trace logs can include sensitive request/response data. Trace was not enabled. The three-day SSH password-expiry notice retained on 23 October is still an unverified lead; no current expiry or causality is established. The captain holds DUO; do not repeatedly ask the owner to inspect a phone they do not hold.

NSCC queue and balance remain unknown. No new NSCC deployment, reservation or PBS receipt exists. Iris job 2294262 continues independently; preserve its frozen payload and allocated slot.
