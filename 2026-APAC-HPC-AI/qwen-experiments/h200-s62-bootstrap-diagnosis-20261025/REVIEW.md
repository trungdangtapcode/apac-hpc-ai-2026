# Failed S62 routes: bounded source diagnosis

Actual 26081 preserves two valid prefill-1→decode routes and two missing prefill-0→decode routes. Four worker/runtime/KV gates passed, but this does not certify KV transfer. Both prefills use the same physical host with distinct bootstrap ports 9000/9001; each decoder is an independent TP4 worker on the other host.

The exact native CommonKVReceiver bootstrap cache key includes bootstrap_addr plus DP/CP/TP identity. Bootstrap URLs use full host:port, so this source does not support blaming a host-only key collision. No live map dump exists; source inspection alone cannot prove actual per-request route choice. Native rank sockets are independently bound dynamic ZMQ ports; raw rank-port maps were not collected. Do not invent a specific port collision.

HTTP/2 probe warnings and initial no-available-worker 503 responses occur across both successful and unsuccessful roles; they are insufficient to explain the selective failure. Final AbortReq KVTransferError logs follow client/deadline termination. They do not identify the initiating fault. Native NIXL agents have UUID names, not a shared role name; this source does not support claiming duplicate agent IDs.

Existing no-model probes 223132 and earlier peer fixtures passed a two-rank/single-peer VRAM/DRAM component on H100. They did not cover the current sixteen-agent/two-prefill/two-decoder fanout or SGLang bootstrap rooms. A separate bounded S68 diagnostic will test direct NIXL registration and fanout with the same four role placements and native prefill 8/decode 0 progress-thread counts, without model loading. This isolates a lower component; even a pass will not repair or validate the failed serving topology. The closed full-topology retry branch remains closed.

Read the S68 PLAN.md and provenance/CPU fixtures. All findings are hypotheses/limits or exact retained source observations; no GPU result, official accuracy or score is claimed. Native sources extracted from /scratch/enroot-images/sglang-harbor.sqsh are hashed in SOURCE-HASHES.json. Raw failed-run evidence remains unchanged in runs/26081.
