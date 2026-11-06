from pathlib import Path
import hashlib,re
FIELDS=("U","p","k","omega","nut","nuTilda")

def sha256(path: Path) -> str:
    digest=hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda:stream.read(2*1024*1024),b""):
            digest.update(block)
    return digest.hexdigest()

def field_snapshot(case: Path, expected_ranks: int) -> dict:
    entries=list(case.glob("processor*"))
    if any(p.is_symlink() for p in entries):
        raise ValueError("processor directory entries may not be symlinks")
    directories={p.name for p in entries if p.is_dir()}
    expected={f"processor{i}" for i in range(expected_ranks)}
    if directories!=expected:
        raise ValueError(f"expected exactly processor0..processor{expected_ranks-1}, found {len(directories)} directories")
    fields={}
    for rank in range(expected_ranks):
        proc=case/f"processor{rank}"
        numeric_times=sorted(p.name for p in proc.iterdir() if p.is_dir() and re.fullmatch(r"[0-9]+(?:\.[0-9]+)?",p.name))
        if numeric_times != ["0"]:
            raise ValueError(f"latestTime source must contain only zero-time fields: {proc}: {numeric_times}")
        for field in FIELDS:
            path=proc/"0"/field
            if not path.is_file() or path.is_symlink():
                raise ValueError(f"missing or symlinked time-zero field: {path}")
            fields[f"processor{rank}/0/{field}"]={"bytes":path.stat().st_size,"sha256":sha256(path)}
    if len(fields)!=expected_ranks*len(FIELDS):
        raise ValueError(f"expected {expected_ranks*len(FIELDS)} zero-time field seals, got {len(fields)}")
    return {"passed":True,"scope":"Byte seals of initialized time-zero fields; solver output writes later times.","rank_count":expected_ranks,"field_count":len(fields),"fields":fields}
