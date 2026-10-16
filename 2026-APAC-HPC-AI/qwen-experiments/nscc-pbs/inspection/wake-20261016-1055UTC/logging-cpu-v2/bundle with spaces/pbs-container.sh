#!/bin/bash
exec python3 -c 'import json,sys;print("CONTAINER_STUB",json.dumps(sys.argv[1:]))' "$@"
