"""Strict comparison of full NVIDIA UUIDs; never accept prefixes or ordinals."""
import re
import uuid


def canonical_uuid(value):
    if not isinstance(value, str):
        raise ValueError('GPU UUID must be a string')
    raw = value.removeprefix('GPU-')
    if re.fullmatch(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', raw) is None:
        raise ValueError('Expected complete non-MIG NVIDIA UUID')
    return str(uuid.UUID(raw))


def require_same_device(allocated, observed):
    expected = canonical_uuid(allocated)
    if canonical_uuid(observed) != expected:
        raise ValueError('GPU UUID differs from scheduler allocation')
    return expected
