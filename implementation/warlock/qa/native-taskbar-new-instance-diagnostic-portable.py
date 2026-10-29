#!/usr/bin/env python3
"""Diagnostic only: GDB is the fixed private fixture's normal-user ancestor."""
import hashlib,os,stat,sys
from pathlib import Path
REPO=Path(__file__).resolve().parents[3]
PINS={'/home/charles/.local/state/warlock-team/20261028/native-rebuild/taskbar-new-instance/diagnostics/ancestor-qualified-sigcont-v1/controller.gdb': 'a195558bb23674f9e6ca216480d58ac5898b1bd32a82a488d4fb178cb4b8f2ce', '/home/charles/.local/state/warlock-team/20261028/native-rebuild/taskbar-new-instance/diagnostics/ancestor-qualified-sigcont-v1/controller.py': 'f1d8319680f5a42afda99b7ccb88e82a437a65be0453f5ab5787536b6667819e', '/home/charles/.local/state/warlock-team/20261028/native-rebuild/taskbar-new-instance/diagnostics/ancestor-qualified-sigcont-v1/diagnostic-runner.py': '382bf92168d9baa6e797c5a8addc691c93fbeb26b466a0576873a4b4f43fc968', '/usr/bin/gdb': 'e95c07efc239f1cc02ef8b85b0ec2e95ee7e5f43a77a2f92a202a5e3e5ffcadf'}
COMMANDS=Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/taskbar-new-instance/diagnostics/ancestor-qualified-sigcont-v1/controller.gdb')
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
    os.execv('/usr/bin/gdb',['/usr/bin/gdb','-nx','-nh','-batch','-iex','set auto-load off','-iex','set debuginfod enabled off','-iex','set startup-with-shell off','-iex','set auto-solib-add off','-iex','set print frame-arguments none','-x',str(COMMANDS)])
if __name__=='__main__':main()
