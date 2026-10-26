#!/usr/bin/env python3
"""Execute worker.sh with local command stubs and assert its real argv contract."""
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
WRAPPER = r'''#!/usr/bin/env bash
set -euo pipefail
if [[ ${1:-} == - ]]; then
  script=$(cat)
  case "$script" in
    *NIXL_PATCH_VERIFIED*) echo "NIXL_PATCH_VERIFIED $QWEN_NIXL_PATCH_SHA256" ;;
    *HPC_OPS_PREFLIGHT_PASSED*) echo "HPC_OPS_PREFLIGHT_PASSED fake-hopper" ;;
    *DYNAMIC_GRAD_MODE_PREFLIGHT_PASSED*) echo "DYNAMIC_GRAD_MODE_PREFLIGHT_PASSED inference_mode=false" ;;
    *) echo "unexpected worker heredoc" >&2; exit 91 ;;
  esac
  exit 0
fi
case "${1:-}" in
  *capture-worker-locality.py|*verify-draft.py|*device_preflight.py) exit 0 ;;
  -m)
    [[ ${2:-} == sglang.launch_server ]] || exit 92
    shift 2
    printf '%s\0' "$@" > "$QWEN_TEST_ARGV_FILE"
    exit 0
    ;;
esac
echo "unexpected worker python invocation: $*" >&2
exit 93
'''

def run(role, port, tp, extra):
    with tempfile.TemporaryDirectory(prefix="equal-tp-worker-argv-") as tmp:
        tmp = Path(tmp)
        wrapper = tmp / "python3"
        wrapper.write_text(WRAPPER)
        wrapper.chmod(0o755)
        cat_stub = tmp / "cat"
        cat_stub.write_text("#!/usr/bin/env bash\ncase \"$1\" in */link_layer) echo InfiniBand;; */state) echo '4: ACTIVE';; *) exec /usr/bin/cat \"$@\";; esac\n")
        cat_stub.chmod(0o755)
        argv_file = tmp / "argv.bin"
        art = tmp / "art"
        art.mkdir()
        env = os.environ.copy()
        env.update({
            "PATH": f"{tmp}:{env['PATH']}",
            "QWEN_BUNDLE": str(ROOT),
            "QWEN_ARTDIR": str(art),
            "QWEN_NIXL_PATCH_SHA256": "912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f",
            "QWEN_TEST_UCX_IB": "ib0:1",
            "QWEN_TEST_ARGV_FILE": str(argv_file),
            "QWEN_RESOURCE_MONITOR": "0",
            "QWEN_ASSIGNED_GPU_INDICES": "0,1,2,3" if role == "prefill-0" else "4,5,6,7",
            "CUDA_VISIBLE_DEVICES": "0,1,2,3,4,5,6,7",
        })
        subprocess.run(["bash", str(ROOT / "worker.sh"), role, str(port), "/fixture/model", str(tp), *extra], env=env, check=True, capture_output=True, text=True)
        args = argv_file.read_bytes().decode().split("\0")[:-1]
        def one(flag):
            assert args.count(flag) == 1, (role, flag, args.count(flag))
            return args[args.index(flag)+1]
        assert one("--model-path") == "/fixture/model"
        assert one("--served-model-name") == "qwen"
        assert one("--dtype") == "bfloat16"
        assert one("--speculative-algorithm") == "EAGLE3"
        assert one("--speculative-num-steps") == "2"
        assert one("--speculative-eagle-topk") == "1"
        assert one("--speculative-num-draft-tokens") == "3"
        assert one("--speculative-draft-model-quantization") == "unquant"
        assert "--speculative-draft-model-path" in args
        assert "--disaggregation-transfer-backend" in args
        assert one("--disaggregation-transfer-backend") == "nixl"
        assert "--cuda-graph-backend-prefill" in args
        assert one("--cuda-graph-backend-prefill") == "disabled"
        return args

prefill = run("prefill-0", 30100, 4, ["--nccl-port", "20001", "--disaggregation-bootstrap-port", "9000"])
decode = run("decode-0", 30200, 4, ["--nccl-port", "20100", "--ep-size", "4", "--max-running-requests", "256"])
assert "--chunked-prefill-size" in prefill and prefill[prefill.index("--chunked-prefill-size")+1] == "4096"
assert "--flashinfer-allreduce-fusion-backend" in decode
assert decode[decode.index("--flashinfer-allreduce-fusion-backend")+1] == "mnnvl"
print("Equal-TP worker argv CPU stub PASS: launcher contract only; no runtime or GPU claim")
