# Portable backup build attempts

2026-11-02T19:02:06.871000+00:00 UTC: first real build stopped before creating output because login Python 3.9 does not support Path.stat(follow_symlinks=False). Replaced the three read-only metadata calls with Path.lstat(), which preserves the no-symlink intent. No GPU work, store mutation, upload or archive content overwrite occurred. The corrected source is captured before rebuilding, so the resulting bundle records a Git commit that contains the fix.
