# Raw evidence retention

At 2026-10-22T14:16:08.683739+00:00, all 90 terminal raw files match the sealed run inventory. The raw request exports, full submitted payload, runtime/transport logs, role resource telemetry, client/phase records, local output/retrieval diagnostics and separate profile evidence are selected for archive capture. The formal review and followup receipts are separate checkpoints.

Git retains safe inline files plus hashes/recovery manifests for larger external objects. The sibling external-object store is not uploaded by Git and still needs a separate off-host copy. No model weights, authentication/session state, private VPN logs or disposable home/runtime caches are part of this selection.
