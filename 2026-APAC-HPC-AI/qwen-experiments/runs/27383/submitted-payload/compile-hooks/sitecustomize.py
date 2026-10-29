"""Chain the image's site hook, then install the rank-local observer."""

import os
from pathlib import Path
import runpy
import hashlib

_SYSTEM_SITE = Path("/etc/python3.12/sitecustomize.py")
_EXPECTED_SYSTEM_SITE_SHA256 = "43d81125d92376b1a69d53a71126a041cc9a18d8080e92dea0a2ae23be138b1e"

if _SYSTEM_SITE.exists():
    _digest = hashlib.sha256(_SYSTEM_SITE.read_bytes()).hexdigest()
    if _digest != _EXPECTED_SYSTEM_SITE_SHA256:
        raise RuntimeError(f"unexpected image sitecustomize source: {_digest}")
    runpy.run_path(str(_SYSTEM_SITE))
else:
    raise RuntimeError(f"image sitecustomize missing: {_SYSTEM_SITE}")

if os.getenv("QWEN_TORCH_COMPILE_OBSERVER") == "1":
    from observer_module import install

    install()
