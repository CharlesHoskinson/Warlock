#!/usr/bin/env python3
"""Run the reviewed machine-local native pin/top independence fixture.

This does not install Warlock or exercise keyboard-only context opening.
"""
import hashlib
import os
from pathlib import Path
import resource
import sys

ROOT = Path(__file__).resolve().parents[3]
TARGET = Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/pin-top-root-v2/runner.py')
PINS = {'/home/charles/.local/state/warlock-team/20261028/native-rebuild/pin-top-root-v2/runner.py': 'dcf78fc3a035778147b977b44db69a9d8c3ab48cd86b558e64deea16a7311447', '/home/charles/.local/state/warlock-team/20261028/native-rebuild/pin-top-root-v2/branch.txt': '05d72e6b6561c6a04c6c18b83d6815fda3a5f6f4f8020b7f8650e36703f552cf', '/home/charles/.local/state/warlock-team/20261028/native-rebuild/pin-top-root-v2/popup_join.py': '5a73d1639c0c2350bad922c5017e902e5aa20e9075c6c91cb3af9d1bd6019aa3', '/home/charles/.local/state/warlock-team/20261028/native-rebuild/pin-top-runtime-root-v1/runtime_candidate.py': '4532b20394a62db96d70923b4efcff10bee0b07c5263efdf6b189d0da1b3a69e', '/home/charles/.local/state/warlock-team/20261028/native-rebuild/pin-top-runtime-root-v1/fresh_candidate.py': '6e1f46eae9fb5fe9e08ff0db1f8746fdbba34adf4af2afa2253d9b4a2be0dfa7'}

def main():
    if sys.argv[1:] or os.environ.get('PYTHONDONTWRITEBYTECODE') != '1':
        raise RuntimeError('Protected no-bytecode pin independence mode only')
    sys.path.insert(0, str(ROOT/'window-integration-qa'))
    from qa_launch import require_qa_scope
    require_qa_scope()
    if resource.getrlimit(resource.RLIMIT_CORE) != (1, 1):
        raise RuntimeError('Protected core limit differs')
    bodies = {}
    for name, expected in PINS.items():
        path = Path(name)
        if path.is_symlink() or not path.is_file():
            raise RuntimeError('Invalid reviewed fixture input '+name)
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected:
            raise RuntimeError('Reviewed fixture input differs '+name)
        bodies[name] = raw
    sys.argv = [str(TARGET)]
    exec(compile(bodies[str(TARGET)], str(TARGET), 'exec'),
         {'__name__': '__main__', '__file__': str(TARGET)})

if __name__ == '__main__':
    main()
