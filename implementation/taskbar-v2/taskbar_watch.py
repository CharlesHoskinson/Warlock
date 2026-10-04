"""Bounded, presentation-only taskbar observations for one Hyprland instance.

Events invalidate observations; they never authorize native effects. Snapshot
queries keep the legacy independent hyprctl calls and action CLI untouched.
"""
import ctypes
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import select
import signal
import socket
import stat
import struct
import subprocess
import sys
import time
import uuid


MAX_EVENT_BUFFER = 65536
MAX_CONTROL_LINE = 64
MAX_SNAPSHOT_BYTES = 4 * 1024 * 1024


class SessionEnded(ValueError):
    pass


class ObservationStopped(BaseException):
    pass


def process_start(pid):
    # comm may contain spaces or ')'; fields after its final ')' start at #3.
    return Path('/proc', str(pid), 'stat').read_text().rsplit(')', 1)[1].split()[19]


class EventConnection:
    def __init__(self, runtime, instance):
        if not instance or not re.fullmatch(r'[A-Za-z0-9_.-]+', instance):
            raise ValueError('A selected HYPRLAND_INSTANCE_SIGNATURE is required')
        self.path = Path(runtime) / 'hypr' / instance / '.socket2.sock'
        self.sock = None
        self.identity = None
        self.peer = None
        self.selected_peer = None
        self.buffer = b''

    def socket_identity(self):
        info = self.path.lstat()
        if not stat.S_ISSOCK(info.st_mode) or info.st_uid != os.getuid():
            raise ValueError('Selected event endpoint must be an owned Unix socket')
        if self.path.resolve() != self.path.absolute():
            raise ValueError('Selected event endpoint may not traverse symlinks')
        return (info.st_dev, info.st_ino)

    def connect(self):
        self.close()
        identity = self.socket_identity()
        stream = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            stream.settimeout(1)
            stream.connect(str(self.path))
            pid, uid, _ = struct.unpack('3i', stream.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
            if uid != os.getuid() or pid <= 0:
                raise ValueError('Event peer belongs to another user')
            self.peer = (pid, process_start(pid))
            if self.selected_peer is not None and self.peer != self.selected_peer:
                raise SessionEnded('Selected compositor process lifetime changed')
            if self.socket_identity() != identity:
                raise ValueError('Event endpoint changed during connection')
            stream.setblocking(False)
            self.identity = identity
            self.sock = stream
            self.selected_peer = self.peer
        except BaseException:
            stream.close()
            raise

    def current(self):
        try:
            return (self.sock is not None and self.socket_identity() == self.identity
                    and process_start(self.peer[0]) == self.peer[1])
        except (OSError, ValueError, IndexError):
            return False

    def read(self):
        data = self.sock.recv(16384)
        if not data:
            raise ConnectionError('Event endpoint disconnected')
        self.buffer += data
        if len(self.buffer) > MAX_EVENT_BUFFER:
            raise ValueError('Event framing exceeded its bound')
        lines = self.buffer.split(b'\n')
        self.buffer = lines.pop()
        # Treat all well-framed events as dirty: unknown new events should not
        # silently leave state stale. Incomplete lines wait for another read.
        return any(b'>>' in line for line in lines)

    def close(self):
        if self.sock is not None:
            self.sock.close()
        self.sock = None
        self.buffer = b''


class ControlLines:
    def __init__(self):
        self.buffer = b''

    def feed(self, data):
        self.buffer += data
        lines = self.buffer.split(b'\n')
        self.buffer = lines.pop()
        if len(self.buffer) > MAX_CONTROL_LINE or any(len(line) > MAX_CONTROL_LINE for line in lines):
            raise ValueError('Observe control line exceeded its bound')
        if any(line != b'refresh' for line in lines):
            raise ValueError('Observe accepts only refresh followed by newline')
        return bool(lines)


def watched_paths(home, config, data):
    runtime = Path(os.environ.get('XDG_RUNTIME_DIR', home / '.cache'))
    files = [config / name for name in ('taskbar-pins.json', 'taskbar-settings.json', 'taskbar-order.json')]
    files += [home / '.config/hypr/reduced-motion', data / 'recently-used.xbel',
              runtime / 'hypr-taskbar-attention.json', runtime / 'hypr-taskbar-launcher.json']
    trees = [Path(root) / 'applications' for root in
             [data, *filter(None, os.environ.get('XDG_DATA_DIRS', '/usr/local/share:/usr/share').split(':'))]]
    snap_state = Path(os.environ.get('HYPR_SNAP_STATE_DIR', runtime / 'hypr-snap-groups')) / 'state.json'
    files.append(snap_state)
    trees += [runtime / 'hypr-window-previews']
    return files, trees, [snap_state]


class FileChanges:
    """One inotify descriptor; ignore self-written session-order and lock files."""
    MASK = (0x00000004 | 0x00000008 | 0x00000040 | 0x00000080
            | 0x00000100 | 0x00000200 | 0x00000400 | 0x00000800)
    ISDIR = 0x40000000
    OVERFLOW = 0x00004000
    IGNORED = 0x00008000

    def __init__(self, files, trees, content_files=()):
        self.files = set(map(Path, files))
        self.trees = set(map(Path, trees))
        self.content_files = set(map(Path, content_files))
        if not self.content_files <= self.files:
            raise ValueError('Content-filtered paths must be explicitly watched files')
        self.content_signatures = {path: self.content_signature(path) for path in self.content_files}
        self.libc = ctypes.CDLL(None, use_errno=True)
        self.libc.inotify_init1.argtypes = [ctypes.c_int]
        self.libc.inotify_add_watch.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_uint32]
        self.libc.inotify_rm_watch.argtypes = [ctypes.c_int, ctypes.c_int]
        self.fd = self.libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
        if self.fd < 0:
            raise OSError(ctypes.get_errno(), 'Cannot initialize file observation')
        self.watches = {}
        self.identities = {}
        try:
            self.refresh()
        except BaseException:
            self.close()
            raise

    def refresh(self):
        desired = set()
        for target in self.files | self.trees:
            parent = target if target in self.trees and target.is_dir() else target.parent
            while not parent.is_dir() and parent != parent.parent:
                parent = parent.parent
            desired.add(parent)
        for tree in self.trees:
            if tree.is_dir():
                desired.update(Path(root) for root, _, _ in os.walk(tree, followlinks=False))
        if len(desired) > 4096:
            raise ValueError('Taskbar directory watch inventory exceeded its bound')
        for wd, directory in list(self.watches.items()):
            try:
                info = directory.stat()
                current = (info.st_dev, info.st_ino)
            except OSError:
                current = None
            if directory not in desired or current != self.identities.get(wd):
                self.libc.inotify_rm_watch(self.fd, wd)
                self.watches.pop(wd, None)
                self.identities.pop(wd, None)
        existing = set(self.watches.values())
        for directory in desired - existing:
            wd = self.libc.inotify_add_watch(self.fd, os.fsencode(directory), self.MASK)
            if wd < 0:
                code = ctypes.get_errno()
                if code not in (errno.ENOENT, errno.ENOTDIR):
                    raise OSError(code, 'Cannot watch ' + str(directory))
            else:
                self.watches[wd] = directory
                info = directory.stat()
                self.identities[wd] = (info.st_dev, info.st_ino)

    def relevant(self, path):
        return (path in self.files or any(path in target.parents for target in self.files)
                or any(path == tree or tree in path.parents or path in tree.parents for tree in self.trees))

    @staticmethod
    def content_signature(path):
        """Suppress only readable finalized JSON with equal content and mode.

        Bad/unreadable/oversized files fall back to inode metadata; their atomic
        replacements remain dirty. This cache is presentation invalidation only.
        """
        def metadata(info):
            return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns,
                    info.st_ctime_ns, info.st_mode, info.st_uid, info.st_gid)
        try:
            before = path.lstat()
        except FileNotFoundError:
            return ('missing',)
        except OSError as error:
            # An uninspectable path must not be silently ignored on a later
            # event. A nonce forces invalidation rather than assuming equality.
            return ('uninspectable', error.errno, uuid.uuid4().hex)
        fallback = ('metadata', metadata(before))
        if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_SNAPSHOT_BYTES:
            return fallback
        fd = None
        try:
            fd = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK)
            selected = os.fstat(fd)
            if metadata(before) != metadata(selected) or not stat.S_ISREG(selected.st_mode):
                return fallback
            parts, size = [], 0
            while size <= MAX_SNAPSHOT_BYTES:
                chunk = os.read(fd, min(65536, MAX_SNAPSHOT_BYTES + 1 - size))
                if not chunk:
                    break
                parts.append(chunk)
                size += len(chunk)
            raw = b''.join(parts)
            if size > MAX_SNAPSHOT_BYTES or metadata(selected) != metadata(os.fstat(fd)):
                return fallback
            json.loads(raw)
            after = path.lstat()
            if metadata(selected) != metadata(after):
                return ('metadata', metadata(after))
            return ('content', hashlib.sha256(raw).hexdigest(), selected.st_mode,
                    selected.st_uid, selected.st_gid)
        except (OSError, ValueError, UnicodeError):
            return fallback
        finally:
            if fd is not None:
                os.close(fd)

    def content_changed(self, path):
        current = self.content_signature(path)
        changed = current != self.content_signatures[path]
        self.content_signatures[path] = current
        return changed

    def read(self):
        dirty, rebuild = False, False
        while True:
            try:
                raw = os.read(self.fd, 65536)
            except BlockingIOError:
                break
            cursor = 0
            while cursor < len(raw):
                wd, mask, _, length = struct.unpack_from('iIII', raw, cursor)
                cursor += 16
                name = os.fsdecode(raw[cursor:cursor + length].split(b'\0', 1)[0])
                cursor += length
                if mask & self.OVERFLOW:
                    dirty = rebuild = True
                if mask & self.IGNORED:
                    self.watches.pop(wd, None)
                    self.identities.pop(wd, None)
                    rebuild = True
                directory = self.watches.get(wd)
                if directory is None:
                    continue
                path = directory / name
                if self.relevant(path) and not name.endswith('.lock'):
                    if path not in self.content_files or self.content_changed(path):
                        dirty = True
                if mask & (self.ISDIR | 0x00000400 | 0x00000800):
                    rebuild = True
        if rebuild:
            self.refresh()
        return dirty

    def close(self):
        if self.fd >= 0:
            os.close(self.fd)
            self.fd = -1


def observe(provider, paths, *, runtime=None, instance=None, input_fd=None, output=None,
            reconcile=15.0, coalesce=0.075, retry=1.0, reconnect_timeout=10.0, should_stop=None):
    """Emit complete JSON snapshots; stdin accepts only bounded refresh lines.

    protocolVersion/epoch/sequence are presentation metadata, never receipts for
    a native action. Epoch is fixed for this process, including reconnects. EOF on stdin ends
    observation so a removed QML service does not leave a helper behind.
    """
    runtime = runtime if runtime is not None else os.environ.get('XDG_RUNTIME_DIR')
    instance = instance if instance is not None else os.environ.get('HYPRLAND_INSTANCE_SIGNATURE')
    if not runtime:
        raise ValueError('XDG_RUNTIME_DIR is required for observe')
    if reconcile <= 0 or coalesce < 0 or retry <= 0 or reconnect_timeout <= 0:
        raise ValueError('Observe intervals must be positive')
    input_fd = sys.stdin.fileno() if input_fd is None else input_fd
    output = sys.stdout if output is None else output
    connection = EventConnection(runtime, instance)
    files = None
    stopped = False
    old_signals = {}

    def stop(signum, frame):
        nonlocal stopped
        stopped = True
        # Unwind subprocess.run as well: its BaseException path terminates and
        # reaps the in-flight read-only query instead of waiting its full budget.
        raise ObservationStopped()

    # The reusable observer can also be tested in a worker thread without
    # installing process-global handlers there.
    if should_stop is None:
        for sig in (signal.SIGTERM, signal.SIGINT):
            old_signals[sig] = signal.signal(sig, stop)
    control = ControlLines()
    epoch, sequence = uuid.uuid4().hex, 0
    dirty = True
    due = next_reconcile = next_retry = 0.0
    unavailable_since = time.monotonic()
    try:
        files = FileChanges(*paths)
        while not stopped and not (should_stop and should_stop()):
            now = time.monotonic()
            if connection.selected_peer is not None:
                try:
                    alive = process_start(connection.selected_peer[0]) == connection.selected_peer[1]
                except (OSError, ValueError, IndexError):
                    alive = False
                if not alive:
                    raise SessionEnded('Selected compositor process exited')
            if connection.sock is not None and not connection.current():
                connection.close()
                next_retry = now
                unavailable_since = now
            if connection.sock is None and now >= next_retry:
                if now - unavailable_since >= reconnect_timeout:
                    raise SessionEnded('Selected event endpoint remained unavailable')
                try:
                    connection.connect()
                    dirty, due = True, now
                except SessionEnded:
                    raise
                except (FileNotFoundError, ConnectionRefusedError, TimeoutError) as error:
                    print('Taskbar observe: ' + str(error), file=sys.stderr)
                    next_retry = now + retry
            now = time.monotonic()
            if connection.sock is not None and (now >= next_reconcile or (dirty and now >= due)):
                try:
                    value = provider()
                    if not isinstance(value, dict):
                        raise ValueError('Snapshot provider must return an object')
                    if not connection.current():
                        raise ConnectionError('Selected instance changed during snapshot')
                    sequence += 1
                    value = dict(value, protocolVersion=1, epoch=epoch, sequence=sequence)
                    raw = json.dumps(value, separators=(',', ':'), allow_nan=False)
                    if len(raw.encode()) > MAX_SNAPSHOT_BYTES:
                        raise ValueError('Snapshot exceeded its output bound')
                    output.write(raw + '\n')
                    output.flush()
                    dirty = False
                    next_reconcile = time.monotonic() + reconcile
                except (ValueError, KeyError, OSError, subprocess.SubprocessError) as error:
                    if isinstance(error, BrokenPipeError):
                        return
                    # No valid fresh snapshot means the UI must lose its last
                    # observation when the tracked process exits.
                    raise
            watched = [input_fd, files.fd]
            if connection.sock is not None:
                watched.append(connection.sock)
            now = time.monotonic()
            deadlines = [now + 0.25]
            if connection.sock is None:
                deadlines.append(next_retry)
            elif dirty:
                deadlines.append(due)
            else:
                deadlines.append(next_reconcile)
            readable, _, _ = select.select(watched, [], [], max(0, min(deadlines) - now))
            if input_fd in readable:
                data = os.read(input_fd, 4096)
                if not data:
                    return
                if control.feed(data) and not dirty:
                    dirty, due = True, time.monotonic() + coalesce
            if files.fd in readable and files.read() and not dirty:
                dirty, due = True, time.monotonic() + coalesce
            if connection.sock is not None and connection.sock in readable:
                try:
                    if connection.read() and not dirty:
                        dirty, due = True, time.monotonic() + coalesce
                except (OSError, ValueError):
                    connection.close()
                    next_retry = time.monotonic() + retry
                    unavailable_since = time.monotonic()
    except ObservationStopped:
        return
    finally:
        connection.close()
        if files is not None:
            files.close()
        for sig, previous in old_signals.items():
            signal.signal(sig, previous)
