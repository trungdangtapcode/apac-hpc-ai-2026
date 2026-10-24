# Repair the performance summarizer path

Control **25930** reached all-rank BF16 readiness and both semantic P/D paths, then completed its raw short AIPerf interval. Our combined launcher failed at the next line: it called `ART/summarize.py` although no helper was copied there. The raw export is retained, but smoke/retrieval did not run and the complete protocol did not pass. Do not treat it as a valid matched control. Dependent candidate **25935** was cancelled pending after Slurm reported `DependencyNeverSatisfied`.

New S57/S58 bundles call the frozen `BUNDLE/summarize.py` directly on both arms. This changes no model setting, workload, quality check or acceptance threshold. The CPU check replays the actual partial export and all three resolved argument records and verifies there is no remaining artifact-directory Python helper reference in the client. It supplies no new GPU result.

Both arms remain unranked N64 performance feasibility, 20/40/30 seconds and fixed 4,000/200 tokens, seed 2026. Official task quality remains unknown, and 25862's strict exact-ID failure remains failed. Candidate admission must bind the actual new control and independently replay its complete passed protocol before model work. No qualified speedup or promotion is in scope.
