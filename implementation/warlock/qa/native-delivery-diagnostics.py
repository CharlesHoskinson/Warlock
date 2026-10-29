#!/usr/bin/env python3
"""Observe first-use delivery receiver and WebKit failure identity on current sources."""
import hashlib
from pathlib import Path
import sys
REPO = Path(__file__).resolve().parents[3]
TARGET = Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/first-use-delivery-current-root-v1/runner.py')
EXPECTED_SHA256 = '5ae3d659cd8bd902fce78ab6e38de2cc3f7e7c4203a20d277c98f47a8bdeeeaf'

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
