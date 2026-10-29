#!/usr/bin/env python3
"""Run the current shared-host invalid-envelope bridge witness."""
import hashlib
from pathlib import Path
import sys
REPO = Path(__file__).resolve().parents[3]
TARGET = Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/arc004-host-admission-root-v4/probe.py')
EXPECTED_SHA256 = '8306cd34e7063212ab07482bd90bef974828ff502c956a2f470acaeb1c26fab0'

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
        raise RuntimeError('Reviewed host-envelope witness changed')
    sys.path.insert(0, str(TARGET.parent))
    sys.argv = [str(TARGET)]
    exec(compile(body, str(TARGET), 'exec'), {'__name__': '__main__', '__file__': str(TARGET), '__package__': None, '__cached__': None})

if __name__ == '__main__':
    main()
