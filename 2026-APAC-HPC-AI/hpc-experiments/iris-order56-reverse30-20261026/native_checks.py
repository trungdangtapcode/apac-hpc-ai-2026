from pathlib import Path
import hashlib,json,re
FIELDS=("U","p","k","omega","nut","nuTilda")
FATAL=re.compile(r"FOAM FATAL|MPI_ABORT|FATAL ERROR",re.I)

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(2 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def field_snapshot(case: Path) -> dict:
    directories = {p.name for p in case.glob("processor*") if p.is_dir() and not p.is_symlink()}
    expected = {f"processor{i}" for i in range(56)}
    if directories != expected:
        raise ValueError(f"expected exactly processor0..processor55, found {len(directories)} directories")
    fields = {}
    for rank in range(56):
        for field in FIELDS:
            path = case / f"processor{rank}" / "0" / field
            if not path.is_file() or path.is_symlink():
                raise ValueError(f"missing or symlinked time-zero field: {path}")
            fields[f"processor{rank}/0/{field}"] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
    if len(fields) != 336:
        raise ValueError(f"expected 336 time-zero field seals, got {len(fields)}")
    return {"passed": True, "scope": "Byte seals of restored time-zero fields; initialization may legitimately change them.",
            "field_count": len(fields), "fields": fields}

def check_probe(run_dir: Path, job_id: str) -> dict:
    probe_path = run_dir / f"{job_id}-mpi-hostnames.log"
    probe = probe_path.read_text(errors="replace")
    observations = []
    for line in probe.splitlines():
        match = re.match(r"^INIT_PROBE\t(\d+)\t([^\s]+)\s*$", line)
        if match:
            observations.append((int(match.group(1)), match.group(2)))
    observed_ranks = [rank for rank, _ in observations]
    hosts = {host for _, host in observations}
    if len(observations) != 56 or set(observed_ranks) != set(range(56)) or len(hosts) != 1:
        raise ValueError(f"MPI hostname probe must show each rank 0..55 exactly once on one node; found {len(observations)} records")
    if "INIT_PROBE_RETURN_CODE=0" not in probe:
        raise ValueError("MPI hostname probe did not return successfully")
    return {"passed": True, "ranks": len(observations), "hosts": sorted(hosts)}

def check_stage_logs(run_dir: Path, job_id: str) -> dict:
    stages = ("renumberMesh", "potentialFoam", "applyBoundaryLayer")
    summaries = {}
    for stage in stages:
        path = run_dir / f"{job_id}-{stage}.log"
        text = path.read_text(errors="replace")
        if "INIT_STAGE_RETURN_CODE=0" not in text:
            raise ValueError(f"{stage}: success sentinel missing")
        if not re.search(r"(?m)^\s*End\s*$", text):
            raise ValueError(f"{stage}: native End marker missing")
        if FATAL.search(text) or re.search(r"died from signal", text, re.I):
            raise ValueError(f"{stage}: fatal marker found")
        if "OPENFOAM=2512" not in text or "scalar=64" not in text:
            raise ValueError(f"{stage}: expected native OpenFOAM 2512 and scalar=64 log metadata")
        if not re.search(r"(?m)^nProcs\s*:\s*56\s*$", text):
            raise ValueError(f"{stage}: log does not report exactly 56 OpenFOAM processes")
        flags = {
            "renumberMesh": r"Exec\s*:\s*renumberMesh\s+-constant\s+-overwrite\s+-parallel\s*$",
            "potentialFoam": r"Exec\s*:\s*potentialFoam\s+-initialiseUBCs\s+-parallel\s*$",
            "applyBoundaryLayer": r"Exec\s*:\s*applyBoundaryLayer\s+-ybl\s+0\.0450244\s+-parallel\s*$",
        }[stage]
        if not re.search(r"(?m)^.*" + flags, text):
            raise ValueError(f"{stage}: actual command and organizer arguments not found in log")
        summaries[stage] = {"log": str(path), "end_marker": True, "openfoam": 2512,
                            "scalar_bits": 64, "nprocs": 56, "fatal_markers": 0}
    probe = check_probe(run_dir, job_id)
    return {"passed": True, "stages": summaries, "mpi_probe": probe}
