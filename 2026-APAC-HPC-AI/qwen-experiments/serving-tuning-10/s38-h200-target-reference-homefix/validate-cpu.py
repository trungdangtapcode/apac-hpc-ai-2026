"""Run CPU-only asset binding, client, and independent head-gate fixtures."""
import unittest


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.discover(".", pattern="test_asset_binding.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
