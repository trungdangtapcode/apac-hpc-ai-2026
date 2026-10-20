# Repair the H200 microbenchmark bind path

Job 24990 failed before Python or any kernel case: exit 127 after 34 seconds on g1. The private writable HOME mount hides the research tree because that tree is inside the same home directory. This is a launcher failure, not a provider performance result. The previous CPU validation exercised the PBS wrapper and missed this Slurm-specific path interaction.

Derived bundle s25-fp8-workbind mounts only the job artifact directory at /work, sets the container working directory there, and invokes /work/submitted/run-micro.sh. A separate private HOME remains for native dependency caches. No real account HOME is exposed. The benchmark, configuration, numerical gates, provider preflight and timing runner are byte-identical to 24990 and accepted H100 screen 222242. The old frozen payload and failure logs remain retained.

The actual scheduler shell passes a CPU fixture that resolves all four payload files through the declared bind mapping and rejects commands under the masked HOME. This validates arguments and paths, not a GPU run. Submit one bounded one-node/eight-H200/ten-minute replacement if at most four other jobs are active. Preserve the four full-model positions. Review all 256 cases and native traces before accepting any kernel comparison; never report this synthetic screen as model goodput or official accuracy.
