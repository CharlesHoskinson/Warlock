#!/usr/bin/env python3
"""Observe genuine catalog failure, keyboard and real AT retry, and recovery."""
import hashlib
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[3]
TARGET = Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/launcher-unavailable-control-name-v1/runner.py')
EXPECTED_SHA256 = '24ae3df31a54e4e9ef40ebdbd655406f582e4ada0018359f4c9fbf64fe978292'


MODE_ARGS = ['--unavailable']


def checked_payload():
    path = Path(TARGET.anchor)
    for component in TARGET.parts[1:]:
        path /= component
        if path.is_symlink():
            raise RuntimeError('Taskbar source symlink refused')
    if not path.is_file():
        raise RuntimeError('Reviewed taskbar source unavailable')
    body = path.read_bytes()
    if hashlib.sha256(body).hexdigest() != EXPECTED_SHA256:
        raise RuntimeError('Reviewed taskbar source changed')
    return body


def main():
    sys.path.insert(0, str(REPO / 'window-integration-qa'))
    from qa_launch import require_qa_scope
    require_qa_scope()
    body = checked_payload()
    sys.path.insert(0, str(TARGET.parent))
    sys.argv = [str(TARGET), *MODE_ARGS]
    namespace = {'__name__': '__main__', '__file__': str(TARGET),
                 '__package__': None, '__cached__': None}
    exec(compile(body, str(TARGET), 'exec'), namespace)


if __name__ == '__main__':
    main()
