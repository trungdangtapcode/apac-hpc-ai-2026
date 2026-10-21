# 21 October: require actual per-pair completion evidence before warmup success

Recorded 2026-10-21T19:59:39.561534+00:00. CPU-only prospective gate; no scheduler or GPU spending.

## Why the gate is necessary

Full integration 223055 printed ALL_PAIRS_WARM despite a real HTTP500 transport
failure because the PBS remote launcher masked the child status. The independent
1600-ID output gate correctly refused promotion, but a success marker gave a
misleading intermediate interpretation. Preserve that failure; do not repair its
already submitted payload in place.

## Exact future change and evidence

The new [helper and integration plan](/home/apacsc42/2026-APAC-HPC-AI/qwen-experiments/pair-warmup-semantic-20261021/PLAN.md) derives the existing temporary
pair-router warmup with the original prompt, max_tokens eight and temperature
zero. It requires HTTP200, one actual assistant completion with nonempty text,
and valid consistent usage with one to eight completion tokens. Receipts bind
all unique endpoint Cartesian pairs to a canonical endpoint inventory hash and
a fresh per-invocation experiment identifier. This identifier is not a secret.

Each actual raw JSON response is retained without headers/authentication state.
The separate allocation-head checker replays the response semantics and hashes;
it rejects missing/duplicate routes, stale identifiers, changed inventories,
invalid counts, response edits and misleading printed success without receipts.
CPU adversarial fixtures pass. No GPU/network response was tested, and the new
helper is not yet deployed into a derived full-model payload.

## Decision and limits

Require this head-side gate before ALL_PAIRS_WARM and the final exact-token
client in a future fresh bundle, with explicit identifier forwarding through
the clean container environment. This prevents false warmup success; it does
not fix the underlying NIXL transport error, prove EAGLE3 output equivalence or
justify an unchanged expensive retry by itself. Current H200/H100 incumbents
and the official accuracy gap remain unchanged.
