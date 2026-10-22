# Dated metadata correction, 22 October

The derived NUMA preparation metadata accidentally retained the default decomposeParDict hash under immutable_input_hashes and omitted that file from changed_text_files. The actual native NUMA dictionary intentionally adds domains (8 16) and weights (1 0.1). The frozen payload-sha256 manifest and full pair accepted-inputs manifest agree on the actual submitted bytes. Audit of all other inherited immutable entries found no mismatch.

This corrects a false inherited immutability claim; it is not evidence of post-submit modification or changed numerical work. Preserve the original metadata, submitted payloads and raw seals. Use the dated JSON correction plus actual payload hashes for recovery. New N256 derivation already removes this changed dictionary from its inherited immutable list. See ../review-audit-20261022/REPORT.md for the independent audit. No new runtime measurement is claimed.
