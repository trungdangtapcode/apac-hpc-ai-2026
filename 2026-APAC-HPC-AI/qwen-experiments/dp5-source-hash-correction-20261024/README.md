# Correct D5 source hash metadata, preserve failed startup

H20025921 failed1:0 after85seconds before model loading. Root had copied a mistyped server_args.py digest into the source contract: `...ffe7b7e8...` instead of actual `...ffe2b7e8...`. Offline named-file extraction from the immutable image shows the retained source itself matches exactly;12otherlisted hashes match. This is a provenance metadata mistake, not a changed image or model incompatibility. The H100 pending parent224552 was cancelled before allocation. Its maximum remains reserved until terminal/accounting reconciliation.

New derived R2 bundles fix the one digest and delay observer imports until actual server launch. All runtime and loaded-expert gates remain. Parent raw artifacts and payloads are unchanged. No successful startup or benchmark result is claimed.
