"""Strict compositor-only private backend selection for mutable legacy launchers."""
import hashlib
import json
import mmap
import os
from pathlib import Path
from qa_launch import require_qa_scope, verify_runtime, verify_parent

STAGE = Path(__file__).resolve().parent / 'aquamarine-nested-lifecycle-v1'

def verify_library():
    manifest = json.loads((STAGE / 'frozen-inputs.json').read_text())
    for path, expected in manifest['inputs'].items():
        if hashlib.sha256(Path(path).read_bytes()).hexdigest() != expected:
            raise RuntimeError('Private backend input changed: ' + path)
    for path, expected in manifest['symlinks'].items():
        p = Path(path)
        if not p.is_symlink() or str(p.readlink()) != expected:
            raise RuntimeError('Private backend loader link changed: ' + path)
    return str(STAGE / 'prefix/lib')

def command(arguments, env):
    require_qa_scope()
    if env.get('AQ_BACKENDS') != 'wayland' or 'AQ_DRM_DEVICES' in env:
        raise RuntimeError('Explicit mandatory Wayland selection required')
    if any(env.get(k) for k in ('LD_PRELOAD', 'LD_AUDIT')):
        raise RuntimeError('Unreviewed loader injection refused')
    verify_runtime(env['XDG_RUNTIME_DIR'])
    verify_parent(env)
    prefix = verify_library()
    # env exec preserves the child PID; dbus and fixtures retain their own libraries.
    library_path = prefix + (':' + env['LD_LIBRARY_PATH'] if env.get('LD_LIBRARY_PATH') else '')
    return ['/usr/bin/env', 'LD_LIBRARY_PATH=' + library_path, '/usr/bin/Hyprland', *arguments]


def actual_mapping_matches(proc, library, expected):
    # Compare the target's backing map against a local read-only mapping from
    # the exact hashed FD. Some filesystems expose a maps device differing
    # from stat.st_dev; comparing two actual maps preserves that identity.
    with library.open('rb') as source:
        if hashlib.sha256(source.read()).hexdigest() != expected:
            raise RuntimeError('Target backend library changed')
        inode = os.fstat(source.fileno()).st_ino
        with mmap.mmap(source.fileno(), min(4096, os.fstat(source.fileno()).st_size), access=mmap.ACCESS_READ):
            def records(path):
                found = set()
                for line in path.read_text().splitlines():
                    fields = line.split(maxsplit=5)
                    if len(fields) == 6 and fields[5] == str(library) and int(fields[4]) == inode:
                        major, minor = fields[3].split(':')
                        found.add((int(major,16), int(minor,16), int(fields[4])))
                return found
            reference = records(Path('/proc/self/maps'))
            return bool(reference and reference.intersection(records(proc/'maps')))
