#!/usr/bin/env bash
# The gateway jumps to Iris only for an interactive login, without a remote command.
set -euo pipefail
exec ssh -tt -i "${IRIS_SSH_KEY:-/home/apacsc42/.ssh/rdmaworkshop30}" \
  -p "${IRIS_GATEWAY_PORT:-22}" -o IdentitiesOnly=yes -o BatchMode=yes \
  -o ConnectTimeout=10 -o StrictHostKeyChecking=yes \
  "${IRIS_ACCOUNT:-rdmaworkshop30}@${IRIS_GATEWAY:-djau.10042008.xyz}"
