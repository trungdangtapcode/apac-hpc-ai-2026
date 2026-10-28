# Continuous decode step lead: hold GPU testing until a real consumer is identified

Recorded 29 October 2026, Vietnam time. The pinned ServerArgs declares `num_continuous_decode_steps`, default 1, described as amortizing scheduling overhead at a possible TTFT cost. This suggested testing 2 on decode only, keeping all workload and model settings. No prior serving 08–11 explicit candidate was found in a bounded config/worker search; this is not exhaustive history proof.

A selective extraction of the actual scheduler.py and disaggregation/decode.py succeeds and both ASTs parse. Neither extracted file contains a reference to `num_continuous_decode_steps`. The main scheduler dispatches decode to `event_loop_overlap_disagg_decode` when overlap is active, which the incumbent uses. The CLI declaration alone therefore does not establish that changing this field affects the actual decode loop. Other modules may consume it; two files are not proof that the feature is globally unused.

Decision: NOT_READY, no GPU submission. Locate and qualify the real consumer/loop and its overlap/graph/P-D compatibility first, or close this unchanged lead. Do not fill a queue with an argument that might be inert. This optional source investigation does not block portable replay 27136 or prefill MNNVL 27138. Those are independently accepted measurements.

Tool correction: the system unsquashfs does not support `-cat`; that initial command printed help and produced an empty redirected file, which was removed. The supported `-processors 2 -no-progress -d FRESH_DEST IMAGE relative/path` form extracted the two pinned files. Extraction logs and SHA256 manifests are retained. No GPU, VPN, PBS charge, submitted payload mutation or other-track change occurred.
