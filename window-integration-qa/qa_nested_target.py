"""Attach legacy cases only to a current owned, scoped QA session descriptor."""
import json
import hashlib
import os
from pathlib import Path
import re
import stat
from qa_launch import require_qa_scope, verify_runtime, verify_parent


def attach():
    require_qa_scope()
    path = Path(os.environ['QA_NESTED_DESCRIPTOR'])
    metadata = path.lstat()
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_uid != os.getuid():
        raise RuntimeError('Descriptor must be an owned regular file, not a symlink')
    content=path.read_bytes()
    row = json.loads(content)
    row['descriptorSHA256']=hashlib.sha256(content).hexdigest()
    runtime = verify_runtime(row['runtime'])
    pid = int(row['pid'])
    proc = Path('/proc') / str(pid)
    if proc.stat().st_uid != os.getuid(): raise RuntimeError('Foreign target process')
    fields = (proc / 'stat').read_text().rsplit(')', 1)[1].split()
    if fields[19] != str(row['start']): raise RuntimeError('Target process was replaced')
    if not re.search(r'/qa-harness\.slice/qa-harness-[A-Za-z0-9_-]+\.scope(?:\n|$)', (proc/'cgroup').read_text()):
        raise RuntimeError('Target compositor is outside QA scope')
    config = Path(row['config'])
    if config.is_symlink() or not config.resolve().is_relative_to(runtime): raise RuntimeError('Foreign target config')
    if str(config).encode() not in (proc/'cmdline').read_bytes().split(b'\0'):
        raise RuntimeError('Target config does not match process')
    # The installed backend ignores AQ_BACKENDS. Require the actual reviewed
    # private mapping, including its kernel map inode, before attaching a case.
    from qa_nested_backend import STAGE, actual_mapping_matches
    library = STAGE/'prefix/lib/libaquamarine.so.0.15.0'
    manifest = json.loads((STAGE/'frozen-inputs.json').read_text())
    if not actual_mapping_matches(proc, library, manifest['inputs'][str(library)]):
        raise RuntimeError('Target does not map the reviewed mandatory Wayland backend')
    env = dict(row['env'])
    if env['XDG_RUNTIME_DIR'] != str(runtime) or env['HYPRLAND_INSTANCE_SIGNATURE'] != row['signature']:
        raise RuntimeError('Descriptor routing mismatch')
    if env['DBUS_SESSION_BUS_ADDRESS'] != 'unix:path=' + str(runtime/'bus'):
        raise RuntimeError('Descriptor must use the owned private bus')
    parent = verify_parent(env)
    if parent['pid'] != pid: raise RuntimeError('Wayland target is a different compositor')
    row['socket'] = env['WAYLAND_DISPLAY']
    return row, env
