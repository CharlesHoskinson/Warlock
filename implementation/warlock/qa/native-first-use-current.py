#!/usr/bin/env python3
"""Observe saved shortcut choices across direct host and authority restart."""
import hashlib
from pathlib import Path
import sys
REPO = Path(__file__).resolve().parents[3]
TARGET = Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/first-use-direct-terra2-v2/runner.py')
EXPECTED_SHA256 = '6e1695061da0ef5be424f75aaa9d63593ee6a8d6348dc619c7050b82267d0084'

def main():
    if sys.argv[1:]:
        raise SystemExit('Use no arguments')
    sys.path.insert(0, str(REPO / 'window-integration-qa'))
    from qa_launch import require_qa_scope
    require_qa_scope()
    cursor = Path(TARGET.anchor)
    for part in TARGET.parts[1:]:
        cursor /= part
        if cursor.is_symlink():
            raise RuntimeError('Reviewed source path contains a symlink')
    body = TARGET.read_bytes()
    if hashlib.sha256(body).hexdigest() != EXPECTED_SHA256:
        raise RuntimeError('Reviewed first-use runner changed')
    sys.path.insert(0, str(TARGET.parent))
    sys.argv = [str(TARGET)]
    exec(compile(body, str(TARGET), 'exec'), {'__name__': '__main__', '__file__': str(TARGET), '__package__': None, '__cached__': None})

if __name__ == '__main__':
    main()
