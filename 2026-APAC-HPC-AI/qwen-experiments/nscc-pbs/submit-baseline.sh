#!/bin/bash -l
set -euo pipefail
PBS_PORT_ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
cd "$PBS_PORT_ROOT"
python3 check-assets.py
(cd baseline-n32 && sha256sum --check SHA256SUMS)
qsub baseline-n32/benchmark.pbs
