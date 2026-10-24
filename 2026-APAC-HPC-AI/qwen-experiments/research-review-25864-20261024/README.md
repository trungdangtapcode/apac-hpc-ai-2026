# Failed FP8 startup validation

Job **25864** failed with exit 1 after **299 seconds** because our inherited allocation checker demanded BF16. All **16** actual role/rank allocation records report FP8 E4M3, as configured.

Model workers did initialize. The semantic and benchmark stages did not complete, so this is a validation bug, not a measured precision-performance result. The corrected S52 replay validates the checker; it does not turn 25864 into a successful benchmark. Frozen payloads and raw evidence remain unchanged. The later actual comparison belongs to job **25920**.
