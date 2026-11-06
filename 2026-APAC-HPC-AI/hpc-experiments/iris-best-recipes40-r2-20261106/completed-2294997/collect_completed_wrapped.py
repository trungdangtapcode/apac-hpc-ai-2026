"""Bounded wrapper preserving remote exceptions in the Iris result frame."""
from pathlib import Path
import runpy
import sys
import textwrap

KIT_TOOLS = Path(__file__).resolve().parents[2] / "tools"
sys.path.insert(0, str(KIT_TOOLS))
import iris_bridge

_original_run_json = iris_bridge.run_json


def run_json_with_bounded_remote_errors(body, timeout=55):
    wrapped = (
        "try:\n"
        + textwrap.indent(body, "    ")
        + "\nexcept Exception as exc:\n"
        + "    result = {'remote_error_type': type(exc).__name__, "
        + "'remote_error': str(exc)[:500]}\n"
    )
    return _original_run_json(wrapped, timeout=timeout)


iris_bridge.run_json = run_json_with_bounded_remote_errors
collector = Path(__file__).with_name("collect_completed.py")
sys.argv = [str(collector)]
runpy.run_path(str(collector), run_name="__main__")
