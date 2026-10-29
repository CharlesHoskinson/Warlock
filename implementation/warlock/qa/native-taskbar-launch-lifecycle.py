#!/usr/bin/env python3
"""Run the reviewed original New Instance journey on the current asset tuple."""
import hashlib
from pathlib import Path
import sys
REPO = Path(__file__).resolve().parents[3]
TARGET = Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/context-keyup-qualified-terra-2-v1/new-instance-runner.py')
EXPECTED_SHA256 = '8d522ad5492ebff48424107eb921efce17e2f4d90c02a99cd750d08462d6a979'

def main():
    if sys.argv[1:] not in ([], ['--at-actions']):
        raise SystemExit('Use no arguments or --at-actions')
    mode = '--at-actions' if sys.argv[1:] else '--keyboard'
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
        raise RuntimeError('Reviewed original journey changed')
    sys.path.insert(0, str(TARGET.parent))
    sys.argv = [str(TARGET), mode]
    exec(compile(body, str(TARGET), 'exec'), {'__name__': '__main__', '__file__': str(TARGET), '__package__': None, '__cached__': None})

if __name__ == '__main__':
    main()
