#!/usr/bin/env python3
"""Diagnostic only: GDB is the fixed private fixture's normal-user ancestor."""
import hashlib,os,stat,sys
from pathlib import Path
REPO=Path('/home/charles/Warlock')
PINS={'/home/charles/.local/state/warlock-team/20261028/native-rebuild/taskbar-new-instance/diagnostics/ancestor-qualified-symbols-v1/controller.gdb': 'c9fce36a0647e002b71be6c13b203b6e2d890cd56a3f81d96efe482db1183fb0', '/home/charles/.local/state/warlock-team/20261028/native-rebuild/taskbar-new-instance/diagnostics/ancestor-qualified-symbols-v1/controller.py': 'c60e5f5675018d389a796863052c735d5b19bf8363cab7892c3377d05b50e7b4', '/home/charles/.local/state/warlock-team/20261028/native-rebuild/taskbar-new-instance/diagnostics/ancestor-qualified-symbols-v1/diagnostic-runner.py': '7bb724351897d2ce3726c8725f018c4d44f2bbf657de92dc20f417f0bf53f1b9', '/usr/bin/gdb': 'e95c07efc239f1cc02ef8b85b0ec2e95ee7e5f43a77a2f92a202a5e3e5ffcadf'}
COMMANDS=Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/taskbar-new-instance/diagnostics/ancestor-qualified-symbols-v1/controller.gdb')
def main():
    if sys.argv[1:]:raise RuntimeError('No diagnostic arguments permitted')
    sys.path.insert(0,str(REPO/'window-integration-qa'))
    from qa_launch import require_qa_scope
    require_qa_scope()
    for name,expected in PINS.items():
        path=Path(name);cursor=Path(path.anchor)
        for part in path.parts[1:]:
            cursor/=part
            if cursor.is_symlink():raise RuntimeError('Diagnostic source symlink refused')
        st=path.stat()
        if not stat.S_ISREG(st.st_mode) or st.st_mode&0o022 or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:raise RuntimeError('Reviewed diagnostic input changed')
        if st.st_uid!=(0 if name=='/usr/bin/gdb' else os.getuid()):raise RuntimeError('Diagnostic input owner changed')
    os.execv('/usr/bin/gdb',['/usr/bin/gdb','-nx','-nh','-batch','-iex','set auto-load off','-iex','set debuginfod enabled off','-iex','set startup-with-shell off','-iex','set auto-solib-add on','-iex','set print frame-arguments none','-x',str(COMMANDS)])
if __name__=='__main__':main()
