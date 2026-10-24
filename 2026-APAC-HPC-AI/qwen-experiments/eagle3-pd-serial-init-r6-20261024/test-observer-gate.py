#!/usr/bin/env python3
"""CPU regression check for observer-gate's packaged helper imports."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


BUNDLE = Path(__file__).resolve().parent
GATE = BUNDLE / "observer-gate.py"


class ObserverGateImportTests(unittest.TestCase):
    def test_pre_warmup_loads_bundle_observer_validator(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = subprocess.run(
                [sys.executable, str(GATE), "pre-warmup", temporary],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(result.returncode, 1)
        self.assertIn("expected 16 metadata receipts before any pair warmup; found 0", result.stderr)
        self.assertNotIn("ModuleNotFoundError", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
