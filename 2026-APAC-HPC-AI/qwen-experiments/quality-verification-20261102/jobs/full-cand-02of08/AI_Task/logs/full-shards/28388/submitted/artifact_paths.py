"""Resolve AIPerf exports stored flat or in one immediate namespace directory."""
from pathlib import Path

EXPORT = 'profile_export_aiperf.json'
REQUESTS = 'profile_export.jsonl'


def _safe_child(parent: Path, child: Path) -> bool:
    """Require a non-symlink child whose resolved path stays inside parent."""
    try:
        resolved_parent = parent.resolve(strict=True)
        resolved_child = child.resolve(strict=True)
        resolved_child.relative_to(resolved_parent)
    except (OSError, RuntimeError, ValueError):
        return False
    return not child.is_symlink() and resolved_child != resolved_parent


def resolve_artifacts(artifacts: Path) -> tuple[Path, Path]:
    """Return the unique complete export pair at root or one child level.

    Candidates are only direct files in ``artifacts`` or direct files in an
    immediate child directory. Deeper recursion is intentionally unsupported.
    A directory containing either expected filename is a candidate and must
    contain both regular, non-symlink files. Multiple complete candidates are
    ambiguous and rejected.
    """
    artifacts = Path(artifacts)
    if artifacts.is_symlink() or not artifacts.is_dir():
        raise ValueError(f'Artifact root is missing or is a symlink: {artifacts}')
    root = artifacts.resolve(strict=True)
    directories = [root]
    for child in sorted(root.iterdir()):
        if child.is_symlink():
            # Reject namespace symlinks rather than allowing hidden candidates.
            raise ValueError(f'Symlink namespace is not allowed under artifact root: {child}')
        if child.is_dir() and _safe_child(root, child):
            directories.append(child)

    complete = []
    incomplete = []
    for directory in directories:
        export = directory / EXPORT
        requests = directory / REQUESTS
        has_export = export.exists() or export.is_symlink()
        has_requests = requests.exists() or requests.is_symlink()
        if not (has_export or has_requests):
            continue
        if has_export and has_requests and _safe_child(root, export) and _safe_child(root, requests):
            if export.is_file() and requests.is_file():
                complete.append((export, requests))
                continue
        incomplete.append(directory)

    if incomplete:
        names = ', '.join(str(p) for p in incomplete)
        raise ValueError(f'Incomplete or unsafe AIPerf export pair in: {names}')
    if len(complete) != 1:
        if not complete:
            raise ValueError(f'No complete AIPerf export pair at {root} or one child level')
        raise ValueError(f'Ambiguous AIPerf export pairs: {len(complete)} candidates under {root}')
    return complete[0]
