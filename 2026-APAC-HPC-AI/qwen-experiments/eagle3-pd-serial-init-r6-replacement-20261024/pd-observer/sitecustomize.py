"""Import-time hook that instruments only the two source-backed SGLang modules."""

import importlib.abc
import importlib.machinery
import hashlib
import os
import sys
from pathlib import Path

from observer import _atomic_json, install_metadata, install_nixl


_EXPECTED = {
    "sglang.srt.disaggregation.utils": "db1b6285e08a6949632d9347f546e1cb290359ca4ad077a1a204af19547caf82",
    "sglang.srt.disaggregation.nixl.conn": "912b7edb95b03604354cc0137f111756ed5bb0eaa91345e713afa53b5bf5024f",
}


def _record_source(fullname, module):
    role = os.environ.get("QWEN_ROLE_NAME", "").strip().lower()
    if role not in {"prefill-0", "prefill-1", "decode-0"}:
        raise RuntimeError("observer source report requires known QWEN_ROLE_NAME")
    artdir = os.environ.get("QWEN_ARTDIR", "").strip()
    if not artdir:
        raise RuntimeError("observer source report requires QWEN_ARTDIR")
    filename = getattr(module, "__file__", None)
    if not filename or not Path(filename).is_file():
        raise RuntimeError(f"observer cannot identify source file for {fullname}")
    path = Path(filename).resolve()
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    expected = _EXPECTED[fullname]
    if digest != expected:
        raise RuntimeError(f"unexpected {fullname} source hash: {digest}")
    safe_name = fullname.rsplit(".", 1)[-1]
    _atomic_json(Path(artdir) / "pd-observer" / "source-modules" / role / f"{safe_name}.json", {
        "schema": "eagle3-pd-source-module-v1",
        "role": role,
        "module": fullname,
        "actual_path": str(path),
        "sha256": digest,
    })


class _Loader(importlib.abc.Loader):
    def __init__(self, wrapped, fullname):
        self._wrapped = wrapped
        self._fullname = fullname

    def create_module(self, spec):
        create = getattr(self._wrapped, "create_module", None)
        return create(spec) if create else None

    def exec_module(self, module):
        self._wrapped.exec_module(module)
        if self._fullname == "sglang.srt.disaggregation.utils":
            install_metadata(module)
            _record_source(self._fullname, module)
        elif self._fullname == "sglang.srt.disaggregation.nixl.conn":
            install_nixl(module)
            _record_source(self._fullname, module)

    def __getattr__(self, name):
        return getattr(self._wrapped, name)


class _Finder(importlib.abc.MetaPathFinder):
    targets = {
        "sglang.srt.disaggregation.utils",
        "sglang.srt.disaggregation.nixl.conn",
    }

    def find_spec(self, fullname, path=None, target=None):
        if fullname not in self.targets:
            return None
        spec = importlib.machinery.PathFinder.find_spec(fullname, path)
        if spec is not None and spec.loader is not None:
            spec.loader = _Loader(spec.loader, fullname)
        return spec


if not any(type(f).__name__ == "_Finder" and f.__class__.__module__ == __name__ for f in sys.meta_path):
    sys.meta_path.insert(0, _Finder())
