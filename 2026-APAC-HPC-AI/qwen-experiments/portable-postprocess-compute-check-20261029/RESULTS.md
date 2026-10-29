# Actual compute reader check passed

Reviewed 29 October 2026 Vietnam time. Job 27152 completed 0:0 in 3 seconds on g1, zero GPUs/two CPUs under 2 minutes. It reproduced the original 27145 alias exception, then successfully ran both corrected readers on both real retained datasets. Logical /home inputs resolved to physical /scratch/home in the actual compute-host namespace. This verifies the postprocessor tail, not a new model run or a successful original GPU allocation.

Corrected raw values remain 3050.225487 and 3055.330517 good output tokens/s, both zero errors/cancellations and about 98.64% joint SLA. Original 27136/27145 FAILED 1:0 states and raw files stay unchanged. No model/P-D inference, hardware utilization, smoke/retrieval or official quality test was performed by this CPU job.

Collected and inspected scheduler accounting, validation.json containing exact logical/canonical roots and both gate/summary records, stdout and stderr. Full team publication has this positive compute evidence with HPC/PPTX bytes unchanged. No further GPU allocation was needed to debug the reader. Raw files and manifest are in runs/27152.
