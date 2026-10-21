#!/usr/bin/env bash
set -euo pipefail
bundle=$1
art=$2
draft=$3
python3 "$bundle/router-preflight.py" round_robin >"$art/router-preflight.log" 2>&1
python3 "$bundle/gateway-echo.py" --out "$art/gateway" >"$art/gateway.log" 2>&1
python3 "$bundle/component.py" --draft "$draft" --out "$art/component.json" >"$art/component.log" 2>&1
