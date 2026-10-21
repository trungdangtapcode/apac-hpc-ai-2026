#!/bin/bash
# Copy the example kit into ./kit. Login node. Do not sbatch this.
# cd to your own folder under apac2026 first. That folder is the work root.
# Not a score. The contest quantity is average wall-clock time per time step.
set -euo pipefail

APAC=/global/exafs/users/rdmaworkshop30/apac2026
SRC=/global/exafs/groups/rdmaworkshop/2026hpcai-openfoam/reference-scripts
GROUP=/global/exafs/groups/rdmaworkshop/2026hpcai-openfoam

how() {
  echo "This folder is visible to everyone on this login. Do not copy the name." >&2
  echo >&2
  echo "  mkdir -p $APAC/blue-kettle" >&2
  echo "  cd $APAC/blue-kettle" >&2
  echo "  ~/00-sync-kit.sh" >&2
  echo "  cd kit" >&2
  echo "  bash ./01-binaries.sh" >&2
  echo "  sbatch 02-toy-stages.sbatch" >&2
  echo >&2
}

if [[ $# -ne 0 ]]; then
  echo "Usage: ~/00-sync-kit.sh" >&2
  how
  exit 1
fi

here=$(pwd)
case "$here" in
  "$GROUP"*)
    echo "This folder is the shared group kit." >&2
    how
    exit 1
    ;;
esac

if [[ "$here" == "$APAC" ]]; then
  echo "Do not use $APAC itself." >&2
  how
  exit 1
fi

case "$here" in
  "$APAC"/*) ;;
  *)
    echo "cd to a folder you created under $APAC first." >&2
    how
    exit 1
    ;;
esac

if [[ "$(basename "$here")" == kit ]]; then
  echo "cd to the folder above kit, then ~/00-sync-kit.sh" >&2
  exit 1
fi

kit="$here/kit"
mkdir -p "$here/runs"
rsync -a --delete \
  --exclude tests/ \
  --exclude 00-sync-kit.sh \
  --exclude runs \
  --exclude runs/ \
  "$SRC"/ "$kit"/
rm -f "$kit/00-sync-kit.sh" "$kit/submit.sh"
if [[ -d "$kit/runs" && ! -L "$kit/runs" ]]; then
  find "$kit/runs" -mindepth 1 -maxdepth 1 -exec mv -f -t "$here/runs" {} +
  rmdir "$kit/runs"
fi
ln -sfn ../runs "$kit/runs"
echo "Kit synced to $kit"
echo "This folder is visible to everyone on this login: $here"
echo "kit/runs -> ../runs (Slurm logs and case trees share that folder)"
echo "Next:"
echo "  cd kit"
echo "  bash ./01-binaries.sh"
echo "  sbatch 02-toy-stages.sbatch"
