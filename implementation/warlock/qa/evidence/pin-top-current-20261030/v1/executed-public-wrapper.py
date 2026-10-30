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
TARGET = Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/pin-top-root-v1/runner.py')
PINS = {'/home/charles/.local/state/warlock-team/20261028/native-rebuild/pin-top-root-v1/runner.py': '4efcd5e2cbe21b7e25c2480d393db48272826e0398a775ed76d594aea38a3546', '/home/charles/.local/state/warlock-team/20261028/native-rebuild/pin-top-root-v1/branch.txt': '2cfe0ebaf3a6b9e15648a1705a37f7262306c019a3ec8eabaaa9a79b478fde85', '/home/charles/.local/state/warlock-team/20261028/native-rebuild/pin-top-root-v1/popup_join.py': '5a73d1639c0c2350bad922c5017e902e5aa20e9075c6c91cb3af9d1bd6019aa3', '/home/charles/.local/state/warlock-team/20261028/native-rebuild/pin-top-runtime-root-v1/runtime_candidate.py': '4532b20394a62db96d70923b4efcff10bee0b07c5263efdf6b189d0da1b3a69e', '/home/charles/.local/state/warlock-team/20261028/native-rebuild/pin-top-runtime-root-v1/fresh_candidate.py': '6e1f46eae9fb5fe9e08ff0db1f8746fdbba34adf4af2afa2253d9b4a2be0dfa7'}

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
