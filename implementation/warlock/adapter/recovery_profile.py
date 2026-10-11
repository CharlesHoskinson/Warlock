#!/usr/bin/env python3
"""Offline component selection and compatible preference recovery.

This local operator command never contacts Elm, the native authority or the
network. It launches only a reviewed, hash-checked local descriptor. Window
policy and effect journals are deliberately absent from recovery profiles.
"""
import argparse
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import secrets
import signal
import stat
import subprocess
import sys
import time

from endpoint import Refused, exact, unique
from taskbar_preferences import Store as PinStore
from shell_preferences import snapshot as settings_snapshot
from shortcut_preferences import snapshot as shortcuts_snapshot
from motion_preferences import snapshot as motion_snapshot

PREFERENCES = ('taskbar.json', 'settings.json', 'shortcuts.json', 'motion.json')
BOUND = 65536


class CommitUnknown(Exception):
    """Selection was renamed, but its directory sync was not confirmed."""


def digest(body):
    return hashlib.sha256(body).hexdigest()


def private(fd, directory=False):
    info = os.fstat(fd)
    valid_type = stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)
    if (not valid_type or info.st_uid != os.getuid() or info.st_mode & 0o077
            or (not directory and info.st_nlink != 1)):
        raise Refused('Recovery storage must be private, owned and unlinked')


def absolute(value):
    if not isinstance(value, (str, Path)):
        raise Refused('Recovery path must be text')
    path = Path(value)
    if not path.is_absolute() or '..' in path.parts:
        raise Refused('Recovery paths must be absolute without traversal')
    return path


def directory(path):
    if path.resolve() != path:
        raise Refused('Recovery storage cannot traverse symlinks')
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        private(fd, True)
        return fd
    except BaseException:
        os.close(fd)
        raise


def read_at(fd, name):
    child = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=fd)
    try:
        private(child)
        body = os.read(child, BOUND + 1)
        if len(body) > BOUND:
            raise Refused('Recovery metadata byte bound')
        return body
    finally:
        os.close(child)


def write_at(fd, name, body):
    if len(body) > BOUND:
        raise Refused('Recovery metadata byte bound')
    child = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                    0o600, dir_fd=fd)
    with os.fdopen(child, 'wb') as stream:
        stream.write(body)
        stream.flush()
        os.fsync(stream.fileno())


def decode(body):
    return json.loads(body, object_pairs_hook=unique)


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(',', ':')) + '\n').encode()


def artifact_sha(path):
    path = absolute(path)
    with path.open('rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise Refused('Recovery artifact must be a regular file')
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def descriptor(value):
    exact(value, ['schema', 'argv', 'cwd', 'files'])
    if type(value['schema']) is not int or value['schema'] != 1:
        raise Refused('Unsupported recovery command schema')
    argv = value['argv']
    if (not isinstance(argv, list) or not 1 <= len(argv) <= 128
            or any(type(arg) is not str or not arg or '\0' in arg or '\n' in arg
                   or len(arg) > 8192 for arg in argv)):
        raise Refused('Recovery command must be a bounded argv array')
    executable = absolute(argv[0])
    if not os.access(executable, os.X_OK):
        raise Refused('Recovery executable is unavailable')
    if not absolute(value['cwd']).is_dir():
        raise Refused('Recovery working directory is unavailable')
    files = value['files']
    if not isinstance(files, dict) or not 1 <= len(files) <= 4096 or argv[0] not in files:
        raise Refused('Recovery descriptor must hash its executable and resources')
    for name, expected in files.items():
        if (type(expected) is not str or len(expected) != 64
                or any(c not in '0123456789abcdef' for c in expected)
                or artifact_sha(name) != expected):
            raise Refused('Recovery artifact changed: ' + name)
    return value


def preference(name, body):
    # Production validators accept compatible legacy appearance without rewriting
    # the original byte copy. Unknown schemas remain untouched in their source.
    if len(body) > (16384 if name == 'taskbar.json' else 4096):
        raise Refused('Preference storage byte bound: ' + name)
    value = decode(body)
    if name == 'taskbar.json':
        exact(value, ['schema', 'revision', 'identities'])
        if type(value['schema']) is not int or value['schema'] != 1:
            raise Refused('Unsupported pin preference schema')
        from taskbar_preferences import snapshot
        snapshot({key: value[key] for key in ('revision', 'identities')})
    else:
        {'settings.json': settings_snapshot, 'shortcuts.json': shortcuts_snapshot,
         'motion.json': motion_snapshot}[name](value)
    return body


class Profile:
    def __init__(self, path):
        self.path = absolute(path)

    @contextlib.contextmanager
    def locked(self):
        root = directory(self.path)
        lock = None
        try:
            lock = os.open('profile.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW,
                           0o600, dir_fd=root)
            private(lock)
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise Refused('Managed component is running or recovery is in progress')
            yield root, lock
        finally:
            if lock is not None:
                os.close(lock)
            os.close(root)

    def manifest(self, root):
        value = decode(read_at(root, 'profile.json'))
        exact(value, ['schema', 'predecessor', 'candidate', 'baseline'])
        if type(value['schema']) is not int or value['schema'] != 1:
            raise Refused('Unsupported recovery profile schema')
        exact(value['baseline'], PREFERENCES)
        return value

    def selection(self, root):
        value = decode(read_at(root, 'selection.json'))
        exact(value, ['schema', 'route', 'stateHome'])
        if (type(value['schema']) is not int or value['schema'] != 1
                or value['route'] not in ('candidate', 'predecessor')
                or type(value['stateHome']) is not str
                or not (value['stateHome'] in ('candidate-state', 'predecessor-state')
                        or (value['stateHome'].startswith('rollback-')
                            and len(value['stateHome']) == 33
                            and all(c in '0123456789abcdef' for c in value['stateHome'][9:])))):
            raise Refused('Invalid component selection')
        return value

    def baseline(self, manifest):
        fd = directory(self.path / 'baseline')
        try:
            bodies = {}
            for name, expected in manifest['baseline'].items():
                if expected is None:
                    try:
                        read_at(fd, name)
                    except FileNotFoundError:
                        continue
                    raise Refused('Unexpected retained preference: ' + name)
                body = read_at(fd, name)
                if digest(body) != expected:
                    raise Refused('Retained preference changed: ' + name)
                bodies[name] = preference(name, body)
            return bodies
        finally:
            os.close(fd)

    def copy_state(self, name, bodies):
        state_home = self.path / name
        state_home.mkdir(mode=0o700)
        stored = state_home / 'warlock'
        stored.mkdir(mode=0o700)
        fd = directory(stored)
        try:
            for filename, body in bodies.items():
                write_at(fd, filename, body)
            os.fsync(fd)
        finally:
            os.close(fd)
        fd = directory(state_home)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def publish(self, root, value):
        temporary = 'selection-' + secrets.token_hex(12) + '.tmp'
        renamed = False
        try:
            write_at(root, temporary, encode(value))
            os.rename(temporary, 'selection.json', src_dir_fd=root, dst_dir_fd=root)
            renamed = True
            os.fsync(root)
        except OSError as error:
            if renamed:
                raise CommitUnknown('Selection renamed; run status to reconcile before proceeding') from error
            raise
        finally:
            if not renamed:
                try:
                    os.unlink(temporary, dir_fd=root)
                except FileNotFoundError:
                    pass

    def prepare(self, predecessor, candidate, source_state):
        predecessor, candidate = descriptor(predecessor), descriptor(candidate)
        source = absolute(source_state)
        if source.resolve() != source:
            raise Refused('Preference source cannot traverse symlinks')
        # All four existing stores share this exact lock. Take one coherent copy;
        # never copy window outcomes, pending requests, grants or recovery journals.
        store = PinStore(str(source))
        fd, lock = store._open()
        try:
            bodies = {}
            for name in PREFERENCES:
                try:
                    bodies[name] = preference(name, read_at(fd, name))
                except FileNotFoundError:
                    pass
        finally:
            os.close(lock)
            os.close(fd)
        if self.path.resolve() != self.path:
            raise Refused('Profile cannot traverse symlinks')
        self.path.mkdir(mode=0o700)  # Exclusive creation; never replaces a profile.
        with self.locked() as (root, lock):
            (self.path / 'baseline').mkdir(mode=0o700)
            fd = directory(self.path / 'baseline')
            try:
                for name, body in bodies.items():
                    write_at(fd, name, body)
                os.fsync(fd)
            finally:
                os.close(fd)
            self.copy_state('predecessor-state', bodies)
            self.copy_state('candidate-state', bodies)
            manifest = {'schema': 1, 'predecessor': predecessor, 'candidate': candidate,
                        'baseline': {name: digest(bodies[name]) if name in bodies else None
                                     for name in PREFERENCES}}
            write_at(root, 'profile.json', encode(manifest))
            selected = {'schema': 1, 'route': 'predecessor', 'stateHome': 'predecessor-state'}
            self.publish(root, selected)
            return {'status': 'Prepared', **selected}

    def status(self):
        # Read-only reconciliation of a possibly uncertain rename; fsync confirms
        # the observed directory entry, without selecting or launching anything.
        root = directory(self.path)
        try:
            value = self.selection(root)
            manifest = self.manifest(root)
            descriptor(manifest[value['route']])
            self.validate_state(value)
            os.fsync(root)
            return {'status': 'Observed', **value}
        finally:
            os.close(root)

    def validate_state(self, selected):
        fd = directory(self.path / selected['stateHome'] / 'warlock')
        try:
            for name in PREFERENCES:
                try:
                    preference(name, read_at(fd, name))
                except FileNotFoundError:
                    pass
        finally:
            os.close(fd)

    def activate(self):
        with self.locked() as (root, lock):
            current = self.selection(root)
            manifest = self.manifest(root)
            descriptor(manifest['candidate'])
            descriptor(manifest['predecessor'])
            self.baseline(manifest)
            if current['route'] == 'candidate':
                os.fsync(root)
                return {'status': 'Unchanged', **current}
            selected = {'schema': 1, 'route': 'candidate', 'stateHome': 'candidate-state'}
            self.validate_state(selected)
            self.publish(root, selected)
            return {'status': 'Selected', **selected}

    def rollback(self):
        with self.locked() as (root, lock):
            current = self.selection(root)
            manifest = self.manifest(root)
            # Never validate the failed candidate's files, state or IPC.
            descriptor(manifest['predecessor'])
            if current['route'] == 'predecessor':
                self.validate_state(current)
                os.fsync(root)
                return {'status': 'Unchanged', **current}
            bodies = self.baseline(manifest)
            state_home = 'rollback-' + secrets.token_hex(12)
            self.copy_state(state_home, bodies)
            selected = {'schema': 1, 'route': 'predecessor', 'stateHome': state_home}
            self.publish(root, selected)
            return {'status': 'Recovered', **selected}

    def run(self):
        with self.locked() as (root, lock):
            selected = self.selection(root)
            manifest = self.manifest(root)
            command = descriptor(manifest[selected['route']])
            self.validate_state(selected)
            os.fsync(root)  # Fresh observation reconciles selection before start.
            env = {**os.environ, 'XDG_STATE_HOME': str(self.path / selected['stateHome'])}
            process = subprocess.Popen(command['argv'], cwd=command['cwd'], env=env,
                                       start_new_session=True, pass_fds=(lock,))
            previous = {}
            def interrupted(signum, frame):
                raise KeyboardInterrupt
            try:
                for signum in (signal.SIGTERM, signal.SIGINT):
                    previous[signum] = signal.signal(signum, interrupted)
                # Retain the group leader's zombie until cleanup: its PID cannot
                # be recycled into an unrelated process group before killpg.
                os.waitid(os.P_PID, process.pid, os.WEXITED | os.WNOWAIT)
            finally:
                for signum, handler in previous.items():
                    signal.signal(signum, handler)
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                deadline = time.monotonic() + 2
                while group_members(process.pid) and time.monotonic() < deadline:
                    time.sleep(0.02)
                if group_members(process.pid):
                    os.killpg(process.pid, signal.SIGKILL)
                code = process.wait(timeout=3)
            return {'status': 'Exited', 'route': selected['route'], 'exitCode': code}


def group_members(group):
    live = []
    for path in Path('/proc').iterdir():
        if not path.name.isdecimal():
            continue
        try:
            fields = (path / 'stat').read_text().rpartition(') ')[2].split()
            if fields[0] != 'Z' and int(fields[2]) == group:
                live.append(int(path.name))
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            pass
    return live


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', required=True)
    sub = parser.add_subparsers(dest='operation', required=True)
    prepare = sub.add_parser('prepare')
    prepare.add_argument('--predecessor', required=True)
    prepare.add_argument('--candidate', required=True)
    prepare.add_argument('--source-state', required=True)
    for operation in ('status', 'activate', 'rollback', 'run'):
        sub.add_parser(operation)
    args = parser.parse_args(argv)
    try:
        profile = Profile(args.profile)
        if args.operation == 'prepare':
            result = profile.prepare(decode(Path(args.predecessor).read_bytes()),
                                     decode(Path(args.candidate).read_bytes()), args.source_state)
        else:
            result = getattr(profile, args.operation)()
        print(json.dumps(result), flush=True)
        return result.get('exitCode', 0) if result.get('exitCode', 0) >= 0 else 1
    except CommitUnknown as error:
        print(json.dumps({'status': 'Unknown', 'detail': str(error)}), flush=True)
        return 3
    except (Refused, OSError, ValueError) as error:
        print(json.dumps({'status': 'Refused', 'detail': str(error)}), flush=True)
        return 2
    except KeyboardInterrupt:
        print(json.dumps({'status': 'Stopped'}), flush=True)
        return 130


if __name__ == '__main__':
    raise SystemExit(main())
