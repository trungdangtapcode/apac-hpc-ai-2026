# Latest AI results and acceptance status

## Accepted portable N64 run: job 28197

The frozen R2 package completed on 16 H200 GPUs in 611 seconds (Slurm state COMPLETED, exit 0:0). The official AIPerf run measured 3,051.518173 good output tokens/s. Of 1,907 requests, 1,881 met the joint latency service-level objective (98.636602%); there were 26 TTFT and 0 ITL violations, with zero errors and cancellations. Both independently validated semantic P/D routes passed, as did summary generation, score gate, and cleanup. This acceptance confirms deployment and benchmark reproducibility for this portable bundle. It is not a matched optimization claim or a new state-of-the-art claim. Official organiser accuracy is UNKNOWN.

## Prior deployment failure: job 28194

Job 28194 ended before AIPerf with curl exit 22. Basic health returned HTTP 200 while model readiness returned 503 during asynchronous initialization. R2 changes only the deployment-readiness gate among runtime files; worker, semantic warmup, readers, and model/environment configuration match the frozen R1 payload. README and checksum files are documentary metadata.

## Interpretation

Job 27378 remains the previously highest completed score in the older research set; that phrasing is now historical because accepted portable job 28197 measured 3,051.518173 tokens/s. Earlier job 27145 reported a higher raw point (3,055.330517 good output tokens/s). Its original allocation failed result postprocessing because of a canonical-path alias; the recovered raw performance export passes the local performance gate, but that allocation was not fully successful. Neither comparison makes 28197 a matched improvement: this is an acceptance replay, not an optimization experiment. H100 results remain a separate platform. The archived job data preserve raw profile exports and losslessly compressed request records; the 228 MB inputs file, model weights, runtime home, and private authentication/cache state are excluded. Hardware telemetry was not collected for job 28197; runtime log sampling is not GPU utilization evidence.
