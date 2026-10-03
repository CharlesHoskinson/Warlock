#!/usr/bin/python3
"""Exact private compositor helper supervisor. Imports have no side effects."""
from pathlib import Path
import fcntl
import hashlib
import json
import os
import re
import shlex
import signal
import socket
import stat
import struct
import sys
import time

QA = Path('/home/hoskinson/window-integration-qa')
sys.path.insert(0, str(QA))
from qa_launch import require_qa_scope, verify_runtime


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def process(pid):
    path = Path('/proc') / str(pid)
    if path.stat().st_uid != os.getuid():
        raise RuntimeError('Foreign helper process')
    fields = (path / 'stat').read_text().rsplit(')', 1)[1].split()
    return {'pid': pid, 'start': fields[19], 'pgid': int(fields[2]),
            'parent': int(fields[1])}


def still_live(row):
    try:
        actual = process(row['pid'])
        return all(actual[k] == row[k] for k in ('pid', 'start', 'pgid'))
    except FileNotFoundError:
        return False


def regular(path, mode):
    info = Path(path).lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != mode:
        raise RuntimeError('Owned exact-mode regular file required: ' + str(path))
    return (info.st_dev, info.st_ino)


def read_config(path):
    path = Path(path)
    identity = regular(path, 0o600)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    with os.fdopen(fd) as stream:
        info=os.fstat(stream.fileno())
        if ((info.st_dev,info.st_ino)!=identity or not stat.S_ISREG(info.st_mode)
                or info.st_uid!=os.getuid() or stat.S_IMODE(info.st_mode)!=0o600):
            raise RuntimeError('Opened helper configuration identity differs')
        row = json.load(stream)
    if regular(path, 0o600) != identity:
        raise RuntimeError('Helper configuration replaced')
    return row


def operation(args):
    if args == ['hydrate']:
        return 'hydrate'
    if len(args) == 4 and args[0] == 'forget-closed' and re.fullmatch(r'0x[0-9a-f]+', args[1]) and re.fullmatch(r'[0-9a-f]+', args[2]) and re.fullmatch(r'[1-9][0-9]*', args[3]):
        return ':'.join(args)
    raise RuntimeError('Unregistered helper operation')


def ancestor_proof(wrapper, config, args):
    compositor = process(config['compositor']['pid'])
    if any(compositor[k] != config['compositor'][k] for k in ('pid', 'start')):
        raise RuntimeError('Compositor identity changed')
    parent = process(wrapper['parent'])
    if parent['pid'] == compositor['pid']:
        return [compositor]
    command = (Path('/proc') / str(parent['pid']) / 'cmdline').read_bytes().rstrip(b'\0').split(b'\0')
    command = [part.decode() for part in command]
    exe = (Path('/proc') / str(parent['pid']) / 'exe').resolve()
    if parent['parent'] != compositor['pid'] or exe != Path('/bin/sh').resolve() or len(command) != 3 or command[1] != '-c' or shlex.split(command[2]) != [config['wrapper'], *args]:
        raise RuntimeError('Helper did not originate from exact compositor invocation')
    return [parent, compositor]


def ipc_proof(config):
    path = Path(config['socket'])
    info = path.lstat()
    identity = [info.st_dev, info.st_ino, info.st_uid]
    if not stat.S_ISSOCK(info.st_mode) or identity != config['socketIdentity']:
        raise RuntimeError('Helper IPC socket replaced')
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(2)
        connection.connect(str(path))
        pid, uid, gid = struct.unpack('3i', connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
        if pid != config['compositor']['pid'] or uid != os.getuid():
            raise RuntimeError('Helper IPC peer mismatch')
        connection.sendall(b'j/version')
        reply = bytearray()
        while chunk := connection.recv(4096):
            reply.extend(chunk)
            if len(reply) > 65536:
                raise RuntimeError('Helper IPC response too large')
    version = json.loads(reply)
    if not isinstance(version, dict) or not version or digest_bytes(reply) != config['versionSHA256']:
        raise RuntimeError('Helper actual compositor version changed')
    after = path.lstat()
    if [after.st_dev, after.st_ino, after.st_uid] != identity:
        raise RuntimeError('Helper IPC socket replaced after full EOF')
    return {'request': 'j/version', 'completeServerEOF': True,
            'peer': {'pid': pid, 'uid': uid, 'gid': gid},
            'socketIdentity': identity, 'replySHA256': digest_bytes(reply)}


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def locked_log(path):
    identity = regular(path, 0o600)
    fd = os.open(path, os.O_RDWR | os.O_NOFOLLOW | os.O_CLOEXEC)
    info = os.fstat(fd)
    if (info.st_dev, info.st_ino) != identity:
        os.close(fd)
        raise RuntimeError('Helper log replaced')
    stream = os.fdopen(fd, 'r+')
    fcntl.flock(stream, fcntl.LOCK_EX)
    return stream


def rows(stream):
    stream.seek(0)
    return [json.loads(line) for line in stream if line.strip()]


def append(stream, row):
    stream.seek(0, os.SEEK_END)
    stream.write(json.dumps(row, sort_keys=True) + '\n')
    stream.flush()
    os.fsync(stream.fileno())


def run(args):
    scope = require_qa_scope()
    config_path = os.environ.get('WINDOW_QA_HELPER_CONFIG', '')
    config = read_config(config_path)
    runtime = verify_runtime(os.environ['XDG_RUNTIME_DIR'])
    home = runtime / 'taskbar-home'
    if Path(config_path) != home / 'helper-config.json' or os.environ.get('HOME') != str(home) or Path(config['wrapper']) != home / '.local/bin/hypr-snap-groups' or config['instance'] != os.environ.get('HYPRLAND_INSTANCE_SIGNATURE'):
        raise RuntimeError('Helper HOME/instance/config mismatch')
    for folder in (home, home / '.local', home / '.local/bin'):
        info = folder.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
            raise RuntimeError('Helper private directory invalid')
    for key in ('wrapper', 'actual'):
        regular(config[key], 0o700)
        if digest(config[key]) != config[key + 'SHA256']:
            raise RuntimeError('Helper executable source changed')
    if Path(config['actual']) != home / '.local/bin/hypr-snap-groups.actual' or Path(config['log']) != home / 'helper-events.jsonl':
        raise RuntimeError('Helper actual/log outside private home')
    wrapper = process(os.getpid())
    ancestry = ancestor_proof(wrapper, config, args)
    if (Path('/proc') / str(config['compositor']['pid']) / 'cgroup').read_text().strip() != scope['cgroup']:
        raise RuntimeError('Helper compositor scope mismatch')
    proof = ipc_proof(config)
    try:
        key = operation(args)
    except RuntimeError:
        with locked_log(config['log']) as stream:
            append(stream, {'event': 'refused', 'args': args, 'wrapper': wrapper,
                            'ancestry': ancestry, 'reason': 'malformed/unregistered operation',
                            'timeNs': time.time_ns()})
        raise
    # Reserve under the existing log lock. No rejected call executes the backend.
    read_fd, write_fd = os.pipe2(os.O_CLOEXEC)
    child = None
    try:
        with locked_log(config['log']) as stream:
            old = rows(stream)
            if key not in config['allowed'] or any(row.get('operation') == key for row in old):
                append(stream, {'event': 'refused', 'operation': key, 'args': args,
                                'wrapper': wrapper, 'ancestry': ancestry,
                                'reason': 'duplicate/unauthorized operation', 'timeNs': time.time_ns()})
                raise RuntimeError('Duplicate or unauthorized helper operation')
            child = os.fork()
            if child == 0:
                os.close(write_fd)
                try:
                    if os.read(read_fd, 1) != b'1':
                        os._exit(125)
                    os.close(read_fd)
                    # Source is rechecked after the registration gate; no run
                    # may substitute a different backend during archival work.
                    regular(config['actual'],0o700)
                    if digest(config['actual'])!=config['actualSHA256']:
                        os._exit(126)
                    os.execv(config['actual'], [config['actual'], *args])
                except BaseException:
                    os._exit(126)
            os.close(read_fd); read_fd = -1
            delegate = process(child)
            append(stream, {'event': 'started', 'operation': key, 'args': args,
                            'wrapper': wrapper, 'delegate': delegate,
                            'ancestry': ancestry, 'ipc': proof, 'scope': scope,
                            'actual': config['actual'], 'actualSHA256': config['actualSHA256'],
                            'timeNs': time.time_ns()})
        os.write(write_fd, b'1'); os.close(write_fd); write_fd = -1
        _, status = os.waitpid(child, 0)
        code = os.waitstatus_to_exitcode(status)
        with locked_log(config['log']) as stream:
            append(stream, {'event': 'terminal', 'operation': key,
                            'wrapper': wrapper, 'delegate': delegate,
                            'exitCode': code, 'timeNs': time.time_ns()})
        if code < 0:
            signal.signal(-code, signal.SIG_DFL)
            os.kill(os.getpid(), -code)
        return code
    finally:
        if read_fd >= 0:
            os.close(read_fd)
        if write_fd >= 0:
            os.close(write_fd)
        # A failed registration cannot leave the gated child waiting forever.
        if child and child > 0:
            try:
                os.waitpid(child, 0)
            except ChildProcessError:
                pass


def summarize(events, allowed, require_all=True):
    starts = [row for row in events if row['event'] == 'started']
    terminals = [row for row in events if row['event'] == 'terminal']
    if len(events) != len(starts) + len(terminals):
        raise RuntimeError('Unknown helper event')
    keys = [row['operation'] for row in starts]
    if len(keys) != len(set(keys)) or not set(keys).issubset(allowed) or (require_all and set(keys) != set(allowed)):
        raise RuntimeError('Missing/duplicate/unregistered helper operation')
    if len(terminals) != len(starts):
        return None
    for start in starts:
        matching = [row for row in terminals if row['operation'] == start['operation']]
        if len(matching) != 1 or matching[0]['exitCode'] != 0 or any(matching[0][key] != start[key] for key in ('wrapper', 'delegate')):
            raise RuntimeError('Helper normal completion mismatch')
        if still_live(start['wrapper']) or still_live(start['delegate']):
            return None
    return {'events': events, 'operations': keys, 'allNormal': True,
            'allExactProcessesGone': True, 'nameExemptions': False}


if __name__ == '__main__':
    try:
        raise SystemExit(run(sys.argv[1:]))
    except Exception as error:
        print('Exact private helper refused: ' + repr(error), file=sys.stderr)
        raise SystemExit(125)
