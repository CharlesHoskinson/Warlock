#!/usr/bin/env python3
"""Observe original launcher initial/loading states on the reviewed current tuple."""
import hashlib
from pathlib import Path
import sys
REPO = Path(__file__).resolve().parents[3]
TARGET = Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/launcher-frozen-policy-states-root-v2/runner.py')
EXPECTED_SHA256 = '0669e7a8a73c20f63f58a97398b88adc076a134d5b5984b60d3a9a0eb04d44c0'

def main():
    if sys.argv[1:]:
        raise SystemExit('Use no arguments')
    mode = '--policy-states'
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
