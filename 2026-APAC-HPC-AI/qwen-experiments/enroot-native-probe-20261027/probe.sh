#!/usr/bin/env bash
set -euo pipefail
umask 077
export ENROOT_DATA_PATH="/tmp/apacsc42-native-enroot-${SLURM_JOB_ID}"
export ENROOT_MAX_PROCESSORS=8
export NVIDIA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:?allocated GPU mask required}"
export NVIDIA_DRIVER_CAPABILITIES=compute,utility
[[ ! -e "$ENROOT_DATA_PATH" && ! -L "$ENROOT_DATA_PATH" ]] || exit 1
mkdir -m 700 "$ENROOT_DATA_PATH"
read -r bs blocks < <(stat -f -c '%S %a' "$ENROOT_DATA_PATH")
(( bs * blocks >= 120 * 1024 * 1024 * 1024 )) || exit 1
name=sglang-probe
cleanup() { enroot remove --force "$name" >/dev/null 2>&1 || :; rmdir "$ENROOT_DATA_PATH" 2>/dev/null || :; }
trap cleanup EXIT
printf 'NATIVE_USER_ENROOT host=%s uid=%s data=%s allocated_gpu=%s\n' "$(hostname)" "$(id -u)" "$ENROOT_DATA_PATH" "$CUDA_VISIBLE_DEVICES"
timeout --signal=TERM --kill-after=5s 140s enroot create --name "$name" /scratch/enroot-images/sglang-harbor.sqsh
[[ -d "$ENROOT_DATA_PATH/$name" ]] || exit 1
timeout --signal=TERM --kill-after=5s 40s enroot start --root --rw \
  --env CUDA_VISIBLE_DEVICES --env NVIDIA_VISIBLE_DEVICES --env NVIDIA_DRIVER_CAPABILITIES \
  "$name" python3 -c 'import json,socket,torch; assert torch.cuda.is_available(); assert torch.cuda.device_count()==1; x=torch.tensor([1.,2.],device="cuda"); assert (x+1).tolist()==[2.,3.]; print(json.dumps({"state":"NATIVE_LOCAL_ENROOT_GPU_PASS","host":socket.gethostname(),"gpu":torch.cuda.get_device_name(0),"torch":torch.__version__,"visible_gpu_count":torch.cuda.device_count(),"tensor_result":(x+1).tolist()}))'
