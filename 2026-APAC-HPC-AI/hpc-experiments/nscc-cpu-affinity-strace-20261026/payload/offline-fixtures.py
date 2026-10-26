#!/usr/bin/env python3
"""Exercise wrapper rank selection and exclusive identity records offline."""
from __future__ import print_function
import json
import os
import pathlib
import subprocess
import sys
import tempfile

def executable(path, body):
    path.write_text("#!/usr/bin/env python3\n" + body, encoding="utf-8")
    path.chmod(0o700)

def run(wrapper, mode, record_dir, probe, strace, native_dir, rank, log):
    env = os.environ.copy()
    env["PMI_RANK"] = str(rank)
    env["FIXTURE_EXEC_LOG"] = str(log)
    return subprocess.call([sys.executable, str(wrapper), mode, str(record_dir),
                            str(probe), str(strace), str(native_dir)], env=env)

def main():
    wrapper = pathlib.Path(__file__).with_name("rank-exec.py")
    with tempfile.TemporaryDirectory(prefix="rank-exec-fixture-") as temp:
        base = pathlib.Path(temp)
        fake = base / "fake-exec.py"
        executable(fake, "import json, os, sys\n"
                         "open(os.environ['FIXTURE_EXEC_LOG'], 'w').write(json.dumps(sys.argv[1:]))\n")
        native = base / "native"
        straced_records = base / "straced-records"
        straced_records.mkdir()
        log = base / "exec.json"

        rc = run(wrapper, "rank0-straced", straced_records, str(fake), str(fake),
                 str(native), 0, log)
        assert rc == 0, "rank zero traced wrapper failed"
        args = json.loads(log.read_text(encoding="utf-8"))
        assert args[:8] == ["-f", "-k", "-ttt", "-e",
                            "trace=sched_setaffinity,sched_getaffinity", "-e",
                            "signal=none", "-o"], args
        assert args[-3:] == ["--", str(fake), str(native)], args
        row = json.loads((straced_records / "rank-0000.json").read_text(encoding="utf-8"))
        assert row["mode"] == "strace" and row["pmi_rank"] == 0
        assert row["pid"] > 0 and row["host"]

        (base / "untraced-records").mkdir()
        rc = run(wrapper, "rank0-straced", base / "untraced-records", str(fake),
                 str(fake), str(native), 1, log)
        assert rc == 0, "nonzero rank wrapper failed"
        args = json.loads(log.read_text(encoding="utf-8"))
        assert args == [str(native)], args
        row = json.loads((base / "untraced-records" / "rank-0001.json").read_text(encoding="utf-8"))
        assert row["mode"] == "native" and row["pmi_rank"] == 1

        duplicate_rc = run(wrapper, "rank0-straced", straced_records, str(fake),
                           str(fake), str(native), 0, log)
        assert duplicate_rc != 0, "duplicate rank identity was accepted"
    print("OFFLINE_WRAPPER_FIXTURES_PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
