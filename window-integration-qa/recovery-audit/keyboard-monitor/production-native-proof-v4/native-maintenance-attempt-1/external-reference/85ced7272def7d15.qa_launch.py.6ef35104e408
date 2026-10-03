"""Shared launch contract for window QA; no process starts during import."""
import os
from contextlib import contextmanager
from pathlib import Path
import re
import resource
import socket
import stat
import struct
import secrets
import shutil


def require_qa_scope():
    cgroup = Path('/proc/self/cgroup').read_text()
    if not re.search(r'/qa-harness\.slice/qa-harness-[A-Za-z0-9_-]+\.scope(?:\n|$)', cgroup):
        raise RuntimeError('Launch through window-integration-qa/qa_run.py in qa-harness.slice')
    diagnostic = os.environ.get('WINDOW_QA_BACKTRACE') == '1'
    expected = resource.RLIM_INFINITY if diagnostic else 1
    if resource.getrlimit(resource.RLIMIT_CORE) != (expected, expected):
        raise RuntimeError('QA scope must set exact soft/hard LimitCORE=' + ('infinity' if diagnostic else '1'))
    return {'cgroup': cgroup.strip(), 'coreLimit': 'infinity' if diagnostic else 1}


def runtime_base():
    base = Path('/run/user') / str(os.getuid())
    check_private_directory(base)
    target = base / 'wqa'
    target.mkdir(mode=0o700, exist_ok=True)
    check_private_directory(target)
    return target


def check_private_directory(path):
    path = Path(path)
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
        raise RuntimeError('Runtime must be an owned, nonsymlink 0700 directory: ' + str(path))


def private_runtime():
    require_qa_scope()
    base = runtime_base()
    # Hyprland's long instance signature must still fit sockaddr_un (107 bytes).
    for _ in range(100):
        path = base / secrets.token_hex(2)
        try: path.mkdir(mode=0o700)
        except FileExistsError: continue
        return path
    raise RuntimeError('Could not allocate a unique short QA runtime')


@contextmanager
def owned_runtime():
    path = private_runtime()
    try: yield str(path)
    finally: shutil.rmtree(path)


def verify_runtime(path):
    path = Path(path)
    check_private_directory(path)
    if path.parent != runtime_base() or not re.fullmatch(r'[0-9a-f]{4}',path.name):
        raise RuntimeError('Use the short owned /run/user/$UID/wqa/<4-hex> runtime')
    return path


def verify_parent(env):
    """Require an explicit live owned Wayland socket; never guess a display."""
    display = env.get('WAYLAND_DISPLAY')
    runtime = env.get('XDG_RUNTIME_DIR')
    if not display or not runtime or env.get('WAYLAND_SOCKET'):
        raise RuntimeError('Explicit WAYLAND_DISPLAY and runtime required; inherited fd rejected')
    path = Path(display) if display.startswith('/') else Path(runtime) / display
    if not path.is_absolute():
        raise RuntimeError('Parent runtime must be absolute')
    before = path.lstat()
    if not stat.S_ISSOCK(before.st_mode) or before.st_uid != os.getuid():
        raise RuntimeError('Parent Wayland socket is foreign, symlinked, or not a socket')
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(.5)
        connection.connect(str(path))
        pid, uid, gid = struct.unpack('3i', connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
        if uid != os.getuid() or pid <= 0:
            raise RuntimeError('Parent Wayland server credentials invalid')
        os.kill(pid, 0)
    after = path.lstat()
    if (before.st_dev, before.st_ino, before.st_uid) != (after.st_dev, after.st_ino, after.st_uid):
        raise RuntimeError('Parent Wayland socket replaced during preflight')
    return {'path': str(path), 'pid': pid, 'uid': uid, 'gid': gid,
            'device': before.st_dev, 'inode': before.st_ino}


def nested_env(parent, runtime):
    require_qa_scope()
    identity = verify_parent(parent)
    runtime = verify_runtime(runtime)
    env = dict(parent)
    for key in ('WAYLAND_SOCKET', 'AQ_DRM_DEVICES', 'DISPLAY', 'XAUTHORITY',
                'HYPRLAND_INSTANCE_SIGNATURE', 'AT_SPI_BUS_ADDRESS'):
        env.pop(key, None)
    env.update(WAYLAND_DISPLAY=identity['path'], XDG_RUNTIME_DIR=str(runtime), AQ_BACKENDS='wayland')
    return env, identity


def verify_device_access():
    """Actual access check; a forwarding/permissions failure stops before launch."""
    nodes = sorted(Path('/dev/dri').glob('renderD*'))
    accessible = []
    for node in nodes:
        try:
            fd = os.open(node, os.O_RDWR | os.O_CLOEXEC)
        except OSError:
            continue
        else:
            os.close(fd)
            accessible.append(str(node))
    if not accessible:
        raise RuntimeError('No accessible DRM render node; run QA outside filesystem/device sandbox')
    return accessible
