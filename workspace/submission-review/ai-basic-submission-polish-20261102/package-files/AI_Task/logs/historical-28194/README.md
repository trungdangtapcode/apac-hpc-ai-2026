# Historical deployment failure: job 28194

This run is not a scored result. Curl exited 22 after the basic health endpoint returned HTTP 200 while model readiness returned HTTP 503 during asynchronous initialization. No AIPerf run or score was produced. The R2 correction adds a model-readiness deployment gate; official worker, semantic warmup and readers were unchanged.
