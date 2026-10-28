#!/usr/bin/env python3
"""Run the reviewed keyboard primary journey on the fresh native tuple."""
import hashlib
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[3]
TARGET = Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/taskbar-primary-keyboard/native-primary-keyboard.py')
EXPECTED_SHA256 = '67f4622fd399bbc59ca03d6ca1bf689e2afa9572f52e3a8a3700355999a382be'


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
