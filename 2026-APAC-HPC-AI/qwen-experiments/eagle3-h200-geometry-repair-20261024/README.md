# H200 EAGLE3 geometry metadata validator repair

Job 25750 retained 32 actual before/after KV registration receipts for 16 ranks. The job ended `FAILED` with exit code `1:0` at the prior validator gate; the preserved stderr excerpt is in `source-job-25750-failure.json`. The prior validator rejected its empty observed layer-ID list because `kv_head_num` and `total_kv_head_num` were `not_collected` on every decode rank. The pinned decode source assigns these fields after KV manager construction, inside the heterogeneous staging branch, so this repair keeps them explicitly uncollected. It does not synthesize observed runtime values.

The validator exception is limited to role `decode-0`, TP 8, PP 0, page size 1, and exactly 190 KV regions. Every such region must be VRAM and have item, page, and token strides of 256 bytes. Prefill receipts remain strict; the exception does not accept missing head values there. Each rank still requires paired before/after receipts and successful registration.

The model config is bound by SHA256 `f056921e486d3e22aed125b5218b87146ea2ac838ccf1521dea5b08f809e8d59`; it records 94 layers, 4 KV heads and head dimension 128. Runtime preflight resolves the scratch model path and checks the config hash. This binds model architecture inputs; it does not populate runtime D-role metadata.

`actual-job-25750-kv-geometry/` is a byte-preserving copy of all 32 source receipts. `test_actual_geometry.py` replays all 32 and includes adversarial D geometry and P strictness cases. The derived S43 bundle retains the inherited BF16, semantic P/D warmup and exact 1600-ID gates. `prepared.json` and `validation.json` describe an unsubmitted frozen candidate. `submit-slurm.py` is adapted controller code and has not been run. No job was submitted.

This is a validator and metadata-evidence repair only. It does not establish model accuracy, EAGLE3 speedup, a serving score, or semantic KV layer order. The receipts report empty layer IDs; ordering remains unproven.
