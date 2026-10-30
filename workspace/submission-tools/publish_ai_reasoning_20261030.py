#!/usr/bin/env python3
"""Publish a reviewed AI-only deck while retaining divergent HPC surfaces."""
from pathlib import Path
import copy
import datetime
import fcntl
import hashlib
import json
import os
import shutil
import stat
import zipfile

from pptx import Presentation

W = Path('/home/apacsc42/workspace')
T = W / 'VNUHCM - TripleU'
Z = W / 'VNUHCM - TripleU.zip'
SIDECAR = W / 'VNUHCM - TripleU.zip.sha256'
O = W / 'submission-review/ai-reasoning-update-20261030'
DECK_REL = 'Presentation/TripleU_APAC2026_Presentation.pptx'
MANIFEST_REL = 'AI_Task/logs/FILE_MANIFEST.json'
SUMS_REL = 'AI_Task/logs/SHA256SUMS'
MUTABLE_ARCHIVE_PATHS = {DECK_REL, MANIFEST_REL, SUMS_REL}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encode_json(value):
    return (json.dumps(value, indent=2) + '\n').encode()


def folder_inventory():
    return {
        str(path.relative_to(T)): path.read_bytes()
        for path in sorted(T.rglob('*')) if path.is_file()
    }


def folder_modes(root):
    return {
        str(path.relative_to(root)): stat.S_IMODE(path.stat().st_mode)
        for path in sorted(root.rglob('*'))
    }


def package_parts(path):
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None, f'Invalid ZIP CRC: {path}'
        return {name: archive.read(name) for name in archive.namelist() if not name.endswith('/')}


def pptx_parts(data):
    import io
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        assert archive.testzip() is None, 'Invalid PowerPoint CRC'
        return {name: archive.read(name) for name in archive.namelist()}


def write_global_manifests(files, now):
    """Rebuild team-wide manifest and sums for one delivery surface."""
    files[MANIFEST_REL] = encode_json({
        'created_utc': now.isoformat(),
        'paths_relative_to_team_directory': True,
        'files': [
            {'path': path, 'bytes': len(data), 'sha256': sha(data)}
            for path, data in sorted(files.items())
            if path not in {MANIFEST_REL, SUMS_REL}
        ],
    })
    files[SUMS_REL] = ''.join(
        f'{sha(data)}  {os.path.relpath(path, "AI_Task/logs")}\n'
        for path, data in sorted(files.items()) if path != SUMS_REL
    ).encode()


def atomic_write(path, data, mode):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f'.{path.name}.ai-reasoning-tmp')
    assert not temp.exists(), f'Unexpected temporary file: {temp}'
    with temp.open('wb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    temp.chmod(mode)
    os.replace(temp, path)


def verify_sum_file(files):
    lines = files[SUMS_REL].decode().splitlines()
    expected = {
        os.path.normpath(os.path.join('AI_Task/logs', line.split('  ', 1)[1])):
            line.split('  ', 1)[0]
        for line in lines
    }
    actual = {path: sha(data) for path, data in files.items() if path != SUMS_REL}
    assert expected == actual, 'Global SHA256SUMS does not match its delivery surface'


def main():
    assert T.is_dir() and Z.is_file() and SIDECAR.is_file()
    assert O.is_dir(), f'Missing reviewed stage: {O}'
    snapshot_path = O / 'HPC_BEFORE.json'
    merge_path = O / 'merge-validation.json'
    staged_deck_path = O / 'TripleU_APAC2026_Presentation.pptx'
    assert snapshot_path.is_file() and merge_path.is_file() and staged_deck_path.is_file(), \
        'Reviewed snapshot, merge validation, and merged deck are required'

    snapshot = json.loads(snapshot_path.read_text())
    merge = json.loads(merge_path.read_text())
    staged_deck = staged_deck_path.read_bytes()
    assert merge.get('passed') is True
    assert merge.get('slides') == 40 and merge.get('updated_ai_slides') == 32
    assert merge.get('preserved_hpc_slides') == 8
    assert sha(staged_deck) == merge.get('pptx_sha256'), 'Merged PPTX hash differs from review'
    assert len(Presentation(staged_deck_path).slides) == 40

    expected_hpc_parts = snapshot['presentation']['hpc_dependency_closure_parts']
    assert len(expected_hpc_parts) == 68, 'Expected the freshly audited 68-part HPC closure'
    merged_parts = pptx_parts(staged_deck)
    assert all(sha(merged_parts[path]) == digest for path, digest in expected_hpc_parts.items())

    lock_path = W / '.submission-publication.lock'
    with lock_path.open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        now = datetime.datetime.now(datetime.timezone.utc)
        before = folder_inventory()
        assert sha(before[DECK_REL]) == snapshot['presentation']['sha256'], \
            'Live presentation changed since the fresh preservation snapshot'

        live_hpc = {p: sha(b) for p, b in before.items() if p.startswith('HPC_Task/')}
        assert live_hpc == snapshot['hpc_task_files'], \
            'Live HPC folder changed since snapshot; stop and re-audit'
        live_modes = folder_modes(T / 'HPC_Task')
        expected_modes = {
            path.removeprefix('HPC_Task/'): mode
            for path, mode in snapshot['hpc_modes'].items()
            if path.startswith('HPC_Task/')
        }
        assert live_modes == expected_modes, 'Live HPC modes changed since snapshot'

        with zipfile.ZipFile(Z) as archive:
            assert archive.testzip() is None
            old_infos = {item.filename: copy.copy(item) for item in archive.infolist()}
            zip_before = {
                name[len(T.name) + 1:]: archive.read(name)
                for name in archive.namelist()
                if name.startswith(T.name + '/') and not name.endswith('/')
            }
        assert SIDECAR.read_text() == f'{sha(Z.read_bytes())}  VNUHCM - TripleU.zip\n', \
            'ZIP checksum sidecar is stale or malformed'
        assert all(name.startswith(T.name + '/') for name in old_infos)
        zip_hpc = {p: sha(b) for p, b in zip_before.items() if p.startswith('HPC_Task/')}
        expected_zip_hpc = {
            name[len(T.name) + 1:]: digest
            for name, digest in snapshot['zip_hpc_files'].items()
            if name.startswith(T.name + '/HPC_Task/')
        }
        assert zip_hpc == expected_zip_hpc, \
            'ZIP HPC payload changed since snapshot; stop and re-audit'
        hpc_divergence = sorted(
            p for p in set(live_hpc) | set(zip_hpc)
            if live_hpc.get(p) != zip_hpc.get(p)
        )

        # The HPC path sets are intentionally divergent. All other paths must
        # agree before publication, and each surface is then updated alone.
        folder_non_hpc = {p for p in before if not p.startswith('HPC_Task/')}
        zip_non_hpc = {p for p in zip_before if not p.startswith('HPC_Task/')}
        assert folder_non_hpc == zip_non_hpc, 'Non-HPC folder/ZIP path sets differ'
        assert all(
            zip_before[p] == before[p]
            for p in folder_non_hpc - MUTABLE_ARCHIVE_PATHS
        ), 'Non-HPC folder/ZIP bytes differ'

        folder_after = dict(before)
        folder_after[DECK_REL] = staged_deck
        write_global_manifests(folder_after, now)
        archive_after = dict(zip_before)
        archive_after[DECK_REL] = staged_deck
        write_global_manifests(archive_after, now)
        verify_sum_file(folder_after)
        verify_sum_file(archive_after)

        # Retain every ZIP member's metadata; the three intentionally changed
        # members keep their original timestamp, mode, and comment as well.
        candidate_zip = O / 'VNUHCM - TripleU.reasoning-reviewed.zip'
        with zipfile.ZipFile(candidate_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as out:
            for name, info in old_infos.items():
                if info.is_dir():
                    out.writestr(copy.copy(info), b'')
            for path, data in sorted(archive_after.items()):
                member = T.name + '/' + path
                assert member in old_infos, f'Unexpected new delivery path: {member}'
                out.writestr(copy.copy(old_infos[member]), data)

        with zipfile.ZipFile(candidate_zip) as archive:
            assert archive.testzip() is None
            candidate_members = {
                name[len(T.name) + 1:]: archive.read(name)
                for name in archive.namelist()
                if name.startswith(T.name + '/') and not name.endswith('/')
            }
            assert candidate_members == archive_after, 'Candidate ZIP payload mismatch'
            candidate_infos = {item.filename: item for item in archive.infolist()}
            for path in set(zip_before) - MUTABLE_ARCHIVE_PATHS:
                name = T.name + '/' + path
                old, new = old_infos[name], candidate_infos[name]
                assert (old.date_time, old.external_attr, old.comment, old.compress_type) == \
                    (new.date_time, new.external_attr, new.comment, new.compress_type), name
            for path in expected_zip_hpc:
                name = T.name + '/' + path
                old, new = old_infos[name], candidate_infos[name]
                assert (old.date_time, old.external_attr, old.comment) == \
                    (new.date_time, new.external_attr, new.comment), name

        assert folder_inventory() == before, 'Concurrent folder edit during preparation'
        stamp = now.strftime('%Y%m%dT%H%M%SZ')
        backup = W / 'submission-archive' / f'before-ai-reasoning-{stamp}'
        backup.mkdir(parents=True, exist_ok=False)
        shutil.copy2(T / DECK_REL, backup / 'TripleU_APAC2026_Presentation.pptx')
        shutil.copy2(Z, backup / Z.name)
        shutil.copy2(SIDECAR, backup / SIDECAR.name)
        shutil.copy2(T / MANIFEST_REL, backup / 'folder-FILE_MANIFEST.json')
        shutil.copy2(T / SUMS_REL, backup / 'folder-SHA256SUMS')

        old_folder_modes = {path: stat.S_IMODE((T / path).stat().st_mode) for path in MUTABLE_ARCHIVE_PATHS}
        old_zip_bytes = Z.read_bytes()
        old_sidecar = SIDECAR.read_bytes()
        old_files = {path: before[path] for path in MUTABLE_ARCHIVE_PATHS}
        replaced = []
        try:
            for path in MUTABLE_ARCHIVE_PATHS:
                atomic_write(T / path, folder_after[path], old_folder_modes[path])
                replaced.append(path)
            atomic_write(Z, candidate_zip.read_bytes(), stat.S_IMODE(Z.stat().st_mode))
            replaced.append('__zip__')
            new_sidecar = (sha(candidate_zip.read_bytes()) + '  VNUHCM - TripleU.zip\n').encode()
            atomic_write(SIDECAR, new_sidecar, stat.S_IMODE(SIDECAR.stat().st_mode))
            replaced.append('__sidecar__')

            actual = folder_inventory()
            assert actual == folder_after
            assert {p: sha(b) for p, b in actual.items() if p.startswith('HPC_Task/')} == live_hpc
            assert folder_modes(T / 'HPC_Task') == live_modes
            with zipfile.ZipFile(Z) as archive:
                assert archive.testzip() is None
                for path, data in archive_after.items():
                    assert archive.read(T.name + '/' + path) == data
            assert SIDECAR.read_text() == f'{sha(Z.read_bytes())}  VNUHCM - TripleU.zip\n'
        except Exception:
            # Restore any partially replaced paths before releasing the lock.
            for item in reversed(replaced):
                if item == '__sidecar__':
                    atomic_write(SIDECAR, old_sidecar, stat.S_IMODE(SIDECAR.stat().st_mode))
                elif item == '__zip__':
                    atomic_write(Z, old_zip_bytes, stat.S_IMODE(Z.stat().st_mode))
                else:
                    atomic_write(T / item, old_files[item], old_folder_modes[item])
            raise

        validation = {
            'passed': True,
            'updated_utc': now.isoformat(),
            'scope': '32 AI slides and team-wide global manifests; no AI_Task implementation or metrics changed',
            'pptx_sha256': sha(staged_deck),
            'original_pptx_sha256': snapshot['presentation']['sha256'],
            'slides': 40,
            'updated_ai_slides': 32,
            'preserved_hpc_slides': 8,
            'hpc_dependency_parts_preserved': len(expected_hpc_parts),
            'hpc_dependency_bytes_identical': True,
            'hpc_folder_file_count': len(live_hpc),
            'hpc_zip_file_count': len(zip_hpc),
            'hpc_folder_hashes_and_modes_preserved': True,
            'hpc_zip_hashes_and_member_metadata_preserved': True,
            'preexisting_hpc_folder_zip_divergence_preserved': True,
            'preexisting_hpc_folder_zip_difference_paths': hpc_divergence,
            'all_other_archive_member_bytes_preserved': True,
            'folder_manifest_sha256': sha(folder_after[MANIFEST_REL]),
            'zip_manifest_sha256': sha(archive_after[MANIFEST_REL]),
            'zip_sha256': sha(Z.read_bytes()),
            'zip_bytes': Z.stat().st_size,
            'backup': str(backup),
            'organiser_upload': False,
        }
        (O / 'publication-validation.json').write_bytes(encode_json(validation))
        print(json.dumps(validation, indent=2))


if __name__ == '__main__':
    main()
