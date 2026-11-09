#!/usr/bin/env python3
"""Read-only checkpoint Boolean preflight; never publishes or acknowledges a wake."""
import argparse
import json
import sys
from pathlib import Path

from owner_route_preflight import SHA, Refused, _read, _sha, _unique

GUARD = 'tools/warlock_continuity.py'
GUARD_SHA256 = 'e1e65923df4c7f43d82739dd4768325d3b405a4ac98381ac24d22eb2aee13d2e'


def inspect(root, checkpoint_relative, expected_sha256):
    """Check representation only; an explicit true blocker stays true."""
    root = Path(root)
    if not root.is_absolute() or root.resolve() != root:
        raise Refused('Expected canonical absolute repository root')
    if not isinstance(expected_sha256, str) or not SHA.fullmatch(expected_sha256):
        raise Refused('Checkpoint digest must be exact SHA256')
    body = _read(root, checkpoint_relative, 1048576)
    if _sha(body) != expected_sha256:
        raise Refused('Checkpoint file digest differs')
    try:
        checkpoint = json.loads(body, object_pairs_hook=_unique)
    except (ValueError, UnicodeError) as problem:
        raise Refused('Checkpoint JSON invalid') from problem
    if not isinstance(checkpoint, dict) or type(checkpoint.get('externalBlocker')) is not bool:
        raise Refused('externalBlocker must be an explicit JSON Boolean; no coercion is performed')
    guard = _read(root, GUARD, 1048576)
    if _sha(guard) != GUARD_SHA256:
        raise Refused('Pinned continuity guard changed')
    if (_read(root, checkpoint_relative, 1048576) != body
            or _read(root, GUARD, 1048576) != guard):
        raise Refused('Input changed during advisory observation')
    return {'schema': 1, 'status': 'consistent-advisory-only',
            'checkpointFileSha256': expected_sha256,
            'externalBlocker': checkpoint['externalBlocker'],
            'guardSha256': GUARD_SHA256,
            'executionAuthorized': False, 'executionPerformed': False,
            'checkpointWritten': False, 'wakeAcknowledged': False,
            'freshGoalVerified': False, 'nativeAuthority': False, 'sourceReady': False,
            'fullCheckpointFreshGoalNonceThreadAndGuardChecksStillRequired': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--checkpoint', type=Path, required=True)
    parser.add_argument('--sha256', required=True)
    args = parser.parse_args()
    try:
        relative = str(args.checkpoint.absolute().relative_to(args.root))
        result = inspect(args.root, relative, args.sha256)
    except (ValueError, OSError) as problem:
        print(json.dumps({'schema': 1, 'status': 'refused', 'error': str(problem),
                          'executionAuthorized': False, 'executionPerformed': False,
                          'checkpointWritten': False, 'wakeAcknowledged': False,
                          'freshGoalVerified': False, 'nativeAuthority': False, 'sourceReady': False}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
