"""Import-time hook that instruments only the two source-backed SGLang modules."""

import importlib.abc
import importlib.machinery
import sys

from observer import install_metadata, install_nixl


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
        elif self._fullname == "sglang.srt.disaggregation.nixl.conn":
            install_nixl(module)

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
