#!/usr/bin/env python3
"""Run the reviewed machine-local current composition attention/AT fixture.

No installation, main-session configuration, or other fixture mode is supported.
The private packet and its historical/runtime dependencies remain by reference.
"""
import hashlib
import os
from pathlib import Path
import resource
import sys

ROOT=Path(__file__).resolve().parents[3]
PACKET=Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/current-native-runtime-attention-root-v5')
PINS={
    'runner.py':'1d91bad01cbdb25fc2ace6896f5a60586d976e68befedca96cae7f004b92bb57',
    'runtime_candidate.py':'ac5eaa594177784b029651a03d8640d457527587df446c3460a67cc74830c128',
    'fresh_candidate.py':'bcc52089ee868c08aa8e5fff367828f81fb5bdf66683e858299c238d6672958a',
    'at-attention.inc':'5b2c814c09e89d4315bfc0c3f881e453cd16af4ed1c392f473a06cbb2f268acd',
}

def main():
    if sys.argv[1:] or os.environ.get('PYTHONDONTWRITEBYTECODE')!='1':
        raise RuntimeError('Protected no-bytecode attention mode only')
    sys.path.insert(0,str(ROOT/'window-integration-qa'))
    from qa_launch import require_qa_scope
    require_qa_scope()
    if resource.getrlimit(resource.RLIMIT_CORE)!=(1,1):
        raise RuntimeError('Protected core limit differs')
    bodies={}
    for name,expected in PINS.items():
        path=PACKET/name
        if path.is_symlink() or not path.is_file():
            raise RuntimeError('Invalid packet input '+name)
        raw=path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=expected:
            raise RuntimeError('Reviewed packet differs '+name)
        bodies[name]=raw
    path=PACKET/'runner.py';sys.argv=[str(path)]
    exec(compile(bodies['runner.py'],str(path),'exec'),{'__name__':'__main__','__file__':str(path)})

if __name__=='__main__':main()
