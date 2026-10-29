#!/usr/bin/env python3
"""Run the compiled native-envelope decoder refusal regression."""
import hashlib
from pathlib import Path
import sys
REPO = Path(__file__).resolve().parents[3]
TARGET = Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/arc004-decoder-root-v3/probe.py')
EXPECTED_SHA256 = '4323e07c6f7e74f426fb8059811f93f239d6273485d4b06cc9e9483f3fa75bf2'

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
        raise RuntimeError('Reviewed decoder fixture changed')
    if hashlib.sha256((TARGET.parent / 'pins.json').read_bytes()).hexdigest() != '62a264a1dca571356740352e6667660c49407e48e0a42931acce5d60be9acba4':
        raise RuntimeError('Reviewed decoder input manifest changed')
    sys.path.insert(0, str(TARGET.parent))
    sys.argv = [str(TARGET)]
    exec(compile(body, str(TARGET), 'exec'), {'__name__': '__main__', '__file__': str(TARGET), '__package__': None, '__cached__': None})

if __name__ == '__main__':
    main()
