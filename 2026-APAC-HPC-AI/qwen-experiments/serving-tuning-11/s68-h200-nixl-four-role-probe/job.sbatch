#!/bin/bash
#SBATCH -J ap42-s68-nixl-fanout
#SBATCH -p hpcai
#SBATCH -N 2
#SBATCH -t 00:05:00
#SBATCH --gres=gpu:8
#SBATCH --exclusive
#SBATCH --propagate=NONE
#SBATCH -o runs/%j.out
#SBATCH -e runs/%j.err
set -euo pipefail
ROOT=$SLURM_SUBMIT_DIR
BUNDLE=$ROOT/serving-tuning-11/s68-h200-nixl-four-role-probe
ART=$ROOT/runs/$SLURM_JOB_ID
EXCHANGE=$ROOT/home/$SLURM_JOB_ID/nixl-exchange
START=$(date +%s)
DEADLINE=$((START+260))
mkdir -p "$ART" "$EXCHANGE"
chmod 700 "$EXCHANGE"
cd "$BUNDLE"
sha256sum -c SHA256SUMS
cp -a "$BUNDLE" "$ART/submitted-payload"
nodes=($(scontrol show hostnames "$SLURM_JOB_NODELIST"))
[[ ${#nodes[@]} == 2 ]] || exit 1
pids=()
cleanup() {
 result=$?
 trap - EXIT
 for pid in "${pids[@]}"; do kill "$pid" 2>/dev/null || :; done
 for pid in "${pids[@]}"; do wait "$pid" 2>/dev/null || :; done
 # Ephemeral peer memory addresses and binary metadata are runtime-only, not backup artifacts.
 rm -rf -- "$EXCHANGE"
 exit "$result"
}
trap cleanup EXIT
for role in prefill-0 prefill-1 decode-0 decode-1; do
 node=0
 [[ $role == decode-* ]] && node=1
 mkdir -p "$ROOT/home/$SLURM_JOB_ID/$role"
 timeout --signal=TERM --kill-after=5s 280 srun --exact -N1 -n1 -w "${nodes[$node]}" --cpu-bind=cores --gres=gpu:4 --cpus-per-task=32 \
   --container-image=/scratch/enroot-images/sglang-harbor.sqsh \
   --container-mounts="/scratch:/scratch,$ROOT:/research,$ROOT/home/$SLURM_JOB_ID/$role:$HOME" \
   bash /research/serving-tuning-11/s68-h200-nixl-four-role-probe/entry.sh "$role" "/research/runs/$SLURM_JOB_ID" "/research/home/$SLURM_JOB_ID/nixl-exchange" "$DEADLINE" \
   >"$ART/$role.log" 2>&1 &
 pids+=("$!")
done
status=0
for pid in "${pids[@]}"; do wait "$pid" || status=1; done
(( status == 0 )) || exit 1
python3 -B "$BUNDLE/probe.py" --art "$ART" --check
