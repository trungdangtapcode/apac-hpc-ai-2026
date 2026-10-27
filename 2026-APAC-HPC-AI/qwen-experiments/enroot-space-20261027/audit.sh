#!/usr/bin/env bash
set -euo pipefail
hostname
id -u
df -B1 /data/enroot/data /tmp /scratch
printf '\nOWN_ENROOT_DIRECTORY\n'
ls -ld /data/enroot/data/user-3042
printf '\nOWN_TOP_LEVEL_SIZES\n'
timeout 70 du -x -h --max-depth=1 /data/enroot/data/user-3042 2>/dev/null | sort -h | tail -18
