#!/usr/bin/env python3
"""Stage selected native CPU records, keeping their origin and limits explicit."""
from pathlib import Path
import hashlib
import json
import shutil

H = Path('/home/apacsc42')
R = H / '2026-APAC-HPC-AI/hpc-experiments'
O = H / 'workspace/submission-review/hpc-update-20261023'
L = O / 'package/HPC_Task/logs'


def main():
    L.mkdir(parents=True, exist_ok=True)
    origins = []

    def copy(source, relative):
        target = L / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        origins.append(dict(path=relative, source=str(source.relative_to(H)),
                            bytes=target.stat().st_size,
                            sha256=hashlib.sha256(target.read_bytes()).hexdigest()))

    selections = [
        ('shared-cpu-intake-20261022', '1n-scotch-25921487', '25921487', 'occ_scotch_1n.pbs'),
        ('shared-cpu-intake-20261022', '2n-scotch-25921492', '25921492', 'occ_scotch_2n.pbs'),
        ('four-node-review-20261023', '4n-scotch-25921488', '25921488', 'occ_scotch_4n.pbs')]
    for collection, run, job, script in selections:
        root = R / collection / 'collected'
        case = root / 'runs' / run
        for folder in ['logFiles', 'postProcessing', 'system', '0.orig', 'constant']:
            for source in sorted((case / folder).rglob('*')):
                if source.is_file() and not source.is_symlink():
                    copy(source, 'native/' + run + '/' + str(source.relative_to(case)))
        for name in [script, 'run_occ_common.sh']:
            source = root / 'job_scripts' / name
            assert source.is_file(), source
            copy(source, 'historical-scripts/' + job + '/' + name)
    copy(R / 'four-node-review-20261023/review.json', 'four-node-comparison.json')
    copy(R / 'shared-cpu-density-review-20261022/review.json', 'one-two-node-comparison.json')
    copy(R / 'access-recovery-20261023T1504/scheduler-status.json', 'confirmation-scheduler-status.json')
    copy(O / 'script-validation.json', 'portable-script-validation.json')
    (L / 'provenance.json').write_text(json.dumps(dict(
        source_repository_commit='84c262431117f5c921db8335e368a12d0e9fa3f0',
        status='Historical native observations; no organizer acceptance claimed',
        scripts_relationship='Historical scripts were collected later, not frozen submitted payloads. '
        'Portable job_scripts are newly derived and did not produce these records.',
        native_gate='Complete original preparation, prescribed work, native timer consistency and finite forces inspected.',
        limits='Old four-node PBS history is unavailable. Final scheduler exit/resources, per-command return '
        'codes, original submitted payload seals and startup physical-core proof are incomplete for those records. '
        'These are internal evidence limitations, not additional official competition rules.',
        independent_confirmation_job='25940700.pbs101', files=origins), indent=2) + '\n')
    (L / 'README.md').write_text('''# OpenFOAM CPU measurements and provenance

The selected candidate is default Scotch with 128 MPI ranks per node on four
ASPIRE-2A CPU nodes (512 total ranks). Historical job **25921488** completed the
native 150-step solve, with 149 timed samples and a mean of **3.677906731 s/step**.
The final dimensionless drag coefficient Cd is 0.2839830076. Lower solver time is
better; Cd is a physical sanity signal, not the performance metric.

The native one/two-node Scotch records are included for scaling context:
25921487 uses one node, 40 steps, 39 timed samples, **14.450756959 s/step**;
25921492 uses two nodes, 80 steps, 79 timed samples, **7.462835189 s/step**.
These are different allocations and prescribed endpoints, so their plotted
differences are descriptive scaling, not an identical-work causal comparison.

The six-configuration four-node comparison is retained in
`four-node-comparison.json`. Raw selected 1/2/4-node native stage logs, original
ASCII case inputs, solverInfo, forces and wall-clock functions are under `native`.
The old collected launcher copies are under `historical-scripts`; they were not
sealed at original submission time. Source-to-package hashes are in `provenance.json`.

All 149 four-node samples are retained. The selected run has median 3.298741570 s,
linearly interpolated p95 3.795740 s and a maximum of 35.883552 s at Time 119.
The script validation report separately labels its nearest-rank p95 convention.
The native short-sample warnings remain. No hardware cause of the timing tail,
independent confidence interval or global optimum has been established.

The older four-node final PBS history is no longer available; native logs do not
prove final scheduler exit status or posted cost. The newly derived portable PBS
scripts in `../job_scripts` have passed offline checks and native-output validator
replays, but they have not yet produced a new compute run. A separate frozen
confirmation, **25940700.pbs101**, was submitted on 23 October and remains Q/q5
in the dated scheduler JSON because node_pool resources are insufficient. Its
performance is pending. This is not a claim of an accepted official score.

The portable script package keeps the complete official initialization, original
v2512 double-precision numerical work and four-node 150-step endpoint. No GPU,
source patch, mesh reduction or removed timing sample is used. Additional
integrity checks are our reproducibility measures, not new organizer rules.
''')
    print(json.dumps(dict(files=len(origins), native_jobs=[x[2] for x in selections],
                          bytes=sum(x['bytes'] for x in origins)), indent=2))


if __name__ == '__main__':
    main()
