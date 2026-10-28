#!/usr/bin/env python3
"""Pinned in-repository entry for the original two-output refusal journey."""
import hashlib
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[3]
DIRECTORY = Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/taskbar-refusal')
PINS = {
    'native-taskbar-refusal.py': 'c8e2bedc6657b365318054c2b9181dcb63c75b2b0e17a54e9ca6ed0f787d549a',
    'native-window-feedback.py': 'ad3ba0929b40f96619859a3bea601aae3dad74c1e5740b849dc9347e767dc9b0',
}


def checked_payloads():
    current = Path(DIRECTORY.anchor)
    for component in DIRECTORY.parts[1:]:
        current /= component
        if current.is_symlink():
            raise RuntimeError('Refusal source directory symlink refused')
    bodies = {}
    for name, expected in PINS.items():
        path = DIRECTORY / name
        if path.is_symlink() or not path.is_file():
            raise RuntimeError('Reviewed refusal source unavailable: ' + name)
        body = path.read_bytes()
        if hashlib.sha256(body).hexdigest() != expected:
            raise RuntimeError('Reviewed refusal source changed: ' + name)
        bodies[name] = body
    return bodies


def main():
    sys.path.insert(0, str(REPO / 'window-integration-qa'))
    from qa_launch import require_qa_scope
    require_qa_scope()
    bodies = checked_payloads()
    target = DIRECTORY / 'native-taskbar-refusal.py'
    sys.path.insert(0, str(DIRECTORY))
    sys.argv[0] = str(target)
    namespace = {'__name__': '__main__', '__file__': str(target),
                 '__package__': None, '__cached__': None}
    # The wrapper also pins the raw framework bytes immediately before compile.
    exec(compile(bodies[target.name], str(target), 'exec'), namespace)


if __name__ == '__main__':
    main()
