"""Select an explicit review stage while preserving dated release inputs."""
from pathlib import Path
import os
import re


DEFAULT_STAGE = 'submission-review/ai-acceptance-update-20261102'


def review_path(workspace, relative=None):
    value = relative or os.environ.get('TRIPLEU_REVIEW_STAGE', DEFAULT_STAGE)
    path = Path(value)
    if path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0] != 'submission-review':
        raise ValueError('Review stage must be relative to workspace/submission-review')
    result = (Path(workspace) / path).resolve()
    result.relative_to(Path(workspace).resolve() / 'submission-review')
    return result


def part_prefix():
    value = os.environ.get('TRIPLEU_PART_PREFIX', 'aia02_')
    if not re.fullmatch(r'[a-zA-Z][a-zA-Z0-9_]*_', value):
        raise ValueError('Invalid PowerPoint part prefix')
    return value
