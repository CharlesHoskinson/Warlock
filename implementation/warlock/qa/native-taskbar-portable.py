#!/usr/bin/env python3
"""Run the reviewed original primary journey on the explicit fresh native tuple."""
import hashlib
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[3]
TARGET = Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/taskbar-qa/native-window-feedback.py')
EXPECTED_SHA256 = '2dd589f4133e1393a3d615c8f5250acc2aa46117fbdbf4c02b81d7f382b82169'


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
    sys.argv[0] = str(TARGET)
    namespace = {'__name__': '__main__', '__file__': str(TARGET),
                 '__package__': None, '__cached__': None}
    exec(compile(body, str(TARGET), 'exec'), namespace)


if __name__ == '__main__':
    main()
