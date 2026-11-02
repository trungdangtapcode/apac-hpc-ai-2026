# Readiness-only repair review

The previous failure was /health200 followed immediately by /v1/models503 during asynchronous worker registration. The gate now requires HTTP success and a JSON data list containing qwen; it checks all existing srun PIDs before each probe, writes only a validated model list to the final artifact and keeps the original job-start+600-second readiness deadline. It changes no model, serving backend, semantic gate or official client flag.

Five local HTTP/step-liveness fixtures passed: 503/empty/malformed/wrong model followed by a valid model; persistent503; persistent wrong model; expired original deadline without a network request; dead worker without a request. Inverse file comparison permits only deploy-and-benchmark.sh and its checksum. Shell syntax and exact setup pass. An independent read-only review found no material flaw. A final failed poll can return slightly beyond the deadline, but a late successful response cannot be accepted; the original allocation hard limit and later gates remain unchanged.

This is CPU/local HTTP qualification, not proof of real gateway activation, GPU inference, performance or official model quality. Require actual new-run artifacts before calling the final entry repaired end to end.
