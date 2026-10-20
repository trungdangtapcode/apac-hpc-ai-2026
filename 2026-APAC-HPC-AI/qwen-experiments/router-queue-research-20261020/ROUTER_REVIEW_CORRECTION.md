# Exact native router representation correction

The first reviewer rejected 222303 because it expected the unit-like Rust Debug text `Some(PowerOfTwo)`. The sealed actual startup reports `Some(PowerOfTwo { load_check_interval_secs: 5 })`; the CPU enum mapping and common hash guard also pass. Preserve the first rejection in 222303-original-router-rejection.json. The corrected reviewer accepts exactly that pinned representation, requires the same main port 8000 and decode_policy None, and retains all worker/protocol/output checks. No submitted payload changed.

The actual policy carries a five-second load check interval. The earlier 30-second load-monitor log described a separate monitoring path and must not be presented as the PowerOfTwo policy interval. Per-dispatch decisions are not collected; startup configuration alone cannot establish the actual cause of a performance change.
