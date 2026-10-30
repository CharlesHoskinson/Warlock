#!/usr/bin/env python3
"""Run the reviewed machine-local compositor-only cancellation ordering fixture.

No installation, main-session configuration, or frontend activation is supported.
The owning build and private parent dependencies remain pinned by reference.
"""
import hashlib,os,resource,sys
from pathlib import Path
PACKET=Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/native-cancellation-orders-root-v2')
PINS={'runner.py':'a8345edea41d9dd88fb5c4673b64285eba64e09736de73f788e488e773cbbf89','runtime_candidate.py':'91a8acd88af2a60075f4ec2ae0c3775dd6917286408052ec338823b18cfcf6de'}
def main():
    if sys.argv[1:] or os.environ.get('PYTHONDONTWRITEBYTECODE')!='1':
        raise SystemExit('Protected no-argument no-bytecode launch required')
    if resource.getrlimit(resource.RLIMIT_CORE)!=(1,1):
        raise SystemExit('Protected core limit differs')
    bodies={}
    for name,expected in PINS.items():
        path=PACKET/name
        if path.is_symlink() or not path.is_file():raise RuntimeError('Invalid reviewed packet file '+name)
        body=path.read_bytes()
        if hashlib.sha256(body).hexdigest()!=expected:raise RuntimeError('Reviewed packet differs '+name)
        bodies[name]=body
    path=PACKET/'runner.py';sys.argv=[str(path)]
    exec(compile(bodies['runner.py'],str(path),'exec'),{'__name__':'__main__','__file__':str(path)})
if __name__=='__main__':main()
