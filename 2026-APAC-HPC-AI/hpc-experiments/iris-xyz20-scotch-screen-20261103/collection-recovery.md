# Terminal collection recovery

On 3 November 2026 the first two terminal transfers failed with the bridge's pre-frame output limit. A later read-only collection succeeded and retained 173 files with byte and SHA-256 verification. The collector was corrected to record an absent fourth arm as NOT_STARTED instead of attempting to read nonexistent telemetry.

A suspected missing frame newline was not reproduced in a local interactive shell; a 100,000-byte remote synthetic JSON reply also passed. The transport cause remains undetermined. No protocol relaxation or bridge patch was applied. Collection retries did not submit, cancel or modify a compute job. Raw authentication output was not retained.
