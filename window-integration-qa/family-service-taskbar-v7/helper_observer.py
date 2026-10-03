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
    if len(args)==7 and args[:3]==['hoskinson.windows','fileDrag','false']:
        for index,value in enumerate(args[3:]):
            if len(value)>20 or not re.fullmatch(r'0|-?[1-9][0-9]*',value):raise RuntimeError('Noncanonical inactive relay integer')
            number=int(value)
            if not -(1<<63)<=number<(1<<63) or (index==3 and number<0):raise RuntimeError('Inactive relay integer outside bounds')
        return 'inactive-fileDrag'
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
    if parent['parent'] != compositor['pid'] or exe != Path('/bin/sh').resolve() or len(command) != 3 or command[1] != '-c' or shlex.split(command[2]) != [config.get('invocation',config['wrapper']), *args]:
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


def cmdline(pid):
    return [part.decode() for part in (Path('/proc')/str(pid)/'cmdline').read_bytes().rstrip(b'\0').split(b'\0')]


def query_environment(pid,config):
    values=dict(part.split(b'=',1) for part in (Path('/proc')/str(pid)/'environ').read_bytes().split(b'\0') if b'=' in part)
    if any(values.get(key.encode())!=value.encode() for key,value in config['queryEnvironment'].items()):
        raise RuntimeError('Taskbar query private environment changed')


def query_ancestor(wrapper,config):
    taskbar=process(wrapper['parent'])
    source=Path(config['queryTaskbar']['path'])
    regular(source,0o700)
    if digest(source)!=config['queryTaskbar']['sha256']:raise RuntimeError('Exact taskbar query source changed')
    executable=(Path('/proc')/str(taskbar['pid'])/'exe').resolve()
    if executable!=Path(config['queryTaskbar']['python']).resolve() or digest(executable)!=config['queryTaskbar']['pythonSHA256']:raise RuntimeError('Taskbar query interpreter changed')
    argv=cmdline(taskbar['pid'])
    if len(argv)!=3 or argv[1:]!=[str(source),'snapshot']:raise RuntimeError('Exact taskbar snapshot argv required')
    query_environment(taskbar['pid'],config)
    candidates=[(kind,row) for kind,row in config['queryRoots'].items() if taskbar['parent']==row['identity']['pid']]
    if len(candidates)!=1:raise RuntimeError('Taskbar query has no exact registered root')
    kind,row=candidates[0];root=process(row['identity']['pid'])
    if any(root[k]!=row['identity'][k] for k in ('pid','start','pgid')):raise RuntimeError('Taskbar root lifetime changed')
    proc=Path('/proc')/str(root['pid'])
    actual_exe=(proc/'exe').resolve()
    if actual_exe!=Path(row['executable']).resolve() or digest(actual_exe)!=row['executableSHA256'] or cmdline(root['pid'])!=row['argv']:
        raise RuntimeError('Taskbar root executable/argv changed')
    if kind=='harness' and digest(row['source'])!=row['sourceSHA256']:raise RuntimeError('Exact harness source changed')
    if kind=='qs' and (row['argv'][1:]!=['-p',row['config']] or digest(Path(row['config'])/'shell.qml')!=row['configSHA256']):raise RuntimeError('Exact QS configuration changed')
    if kind=='qs':query_environment(root['pid'],config)
    if (proc/'cgroup').read_text().strip()!=(Path('/proc/self/cgroup').read_text().strip()):raise RuntimeError('Taskbar root scope changed')
    return kind,[taskbar,root]


def run(args, entry=None):
    scope = require_qa_scope()
    config_path = os.environ.get('WINDOW_QA_HELPER_CONFIG', '')
    shared = read_config(config_path)
    runtime = verify_runtime(os.environ['XDG_RUNTIME_DIR'])
    home = runtime / 'taskbar-home'
    if Path(config_path)!=home/'helper-config.json' or os.environ.get('HOME')!=str(home) or shared['instance']!=os.environ.get('HYPRLAND_INSTANCE_SIGNATURE') or Path(shared['log'])!=home/'helper-events.jsonl':
        raise RuntimeError('Helper HOME/instance/config mismatch')
    selected=Path(sys.argv[0] if entry is None else entry)
    names={'snap':'hypr-snap-groups','shell':'omarchy-shell'}
    if set(shared['helpers'])!=set(names):raise RuntimeError('Exact two registered helper sources required')
    chosen=[kind for kind,name in names.items() if selected==home/'.local/bin'/name]
    if len(chosen)!=1:raise RuntimeError('Unknown exact helper entry')
    kind=chosen[0];config={**shared,**shared['helpers'][kind]}
    if Path(config['wrapper'])!=selected or Path(config['actual'])!=selected.with_name(selected.name+'.actual'):
        raise RuntimeError('Helper source outside selected private HOME')
    # The envelope authorizes only a durable refusal record, never execution
    # with unsafe modes. Own paths/source/ancestry/socket remain mandatory.
    for folder in (home, home/'.local', home/'.local/bin'):
        info=folder.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid!=os.getuid():raise RuntimeError('Helper private directory identity invalid')
    regular(config['wrapper'],0o700)
    if digest(config['wrapper'])!=config['wrapperSHA256']:raise RuntimeError('Helper observer source changed')
    wrapper=process(os.getpid());query=args==['list','--json']
    query_kind=None
    if query:
        if kind!='snap':raise RuntimeError('Query belongs to exact Snap helper')
        query_kind,ancestry=query_ancestor(wrapper,config)
    else:ancestry=ancestor_proof(wrapper,config,args)
    if (Path('/proc')/str(config['compositor']['pid'])/'cgroup').read_text().strip()!=scope['cgroup']:
        raise RuntimeError('Helper compositor scope mismatch')
    proof=ipc_proof(config)
    try:
        for folder in (home,home/'.local',home/'.local/bin'):
            if stat.S_IMODE(folder.lstat().st_mode)!=0o700:raise RuntimeError('Helper private directory invalid')
        if kind=='shell' and os.environ.get('PATH','').split(':')[0]!=str(home/'.local/bin'):
            raise RuntimeError('Inactive relay must resolve private wrapper first')
        regular(config['actual'],0o700)
        if digest(config['actual'])!=config['actualSHA256']:raise RuntimeError('Helper executable source changed')
        key=('harness-list-json' if query_kind=='harness' else 'list-json:'+str(wrapper['pid'])+':'+wrapper['start']) if query else operation(args)
        if not query and (kind=='shell')!=(key=='inactive-fileDrag'):raise RuntimeError('Operation belongs to another exact helper')
    except RuntimeError as error:
        with locked_log(config['log']) as stream:
            append(stream,{'event':'refused','args':args,'helper':kind,'wrapper':wrapper,'ancestry':ancestry,'ipc':proof,'reason':str(error),'timeNs':time.time_ns()})
        raise
    # Reserve under the existing log lock. No rejected call executes the backend.
    read_fd, write_fd = os.pipe2(os.O_CLOEXEC)
    child = None
    try:
        with locked_log(config['log']) as stream:
            old = rows(stream)
            if (not query and key not in config['allowed']) or any(row.get('operation') == key for row in old):
                append(stream, {'event': 'refused', 'operation': key, 'args': args,
                                'helper':kind, 'wrapper': wrapper, 'ancestry': ancestry,
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
                            'class':'query' if query else 'compositor','queryRoot':query_kind,'helper':kind, 'wrapper': wrapper, 'delegate': delegate,
                            'ancestry': ancestry, 'ipc': proof, 'scope': scope,
                            'actual': config['actual'], 'actualSHA256': config['actualSHA256'],
                            'timeNs': time.time_ns()})
        os.write(write_fd, b'1'); os.close(write_fd); write_fd = -1
        _, status = os.waitpid(child, 0)
        code = os.waitstatus_to_exitcode(status)
        with locked_log(config['log']) as stream:
            append(stream, {'event': 'terminal', 'operation': key,
                            'class':'query' if query else 'compositor','queryRoot':query_kind,'helper':kind, 'wrapper': wrapper, 'delegate': delegate,
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


def summarize(events, allowed, require_all=True,expect_harness=False):
    starts = [row for row in events if row['event'] == 'started']
    terminals = [row for row in events if row['event'] == 'terminal']
    if len(events) != len(starts) + len(terminals):
        raise RuntimeError('Unknown helper event')
    comp=[row for row in starts if row.get('class','compositor')=='compositor']
    queries=[row for row in starts if row.get('class')=='query']
    if len(comp)+len(queries)!=len(starts):raise RuntimeError('Unknown helper authority class')
    keys = [row['operation'] for row in comp]
    query_keys=[row['operation'] for row in queries]
    if len(query_keys)!=len(set(query_keys)) or any(row.get('queryRoot') not in ('qs','harness') for row in queries):raise RuntimeError('Duplicate/unknown query role')
    harness=[row for row in queries if row.get('queryRoot')=='harness']
    if len(harness)>1 or (expect_harness and len(harness)!=1):raise RuntimeError('Exactly one harness query required')
    if len(keys) != len(set(keys)) or not set(keys).issubset(allowed) or (require_all and set(keys) != set(allowed)):
        raise RuntimeError('Missing/duplicate/unregistered helper operation')
    if len(terminals) != len(starts):
        return None
    for start in starts:
        matching = [row for row in terminals if row['operation'] == start['operation']]
        if len(matching) != 1 or matching[0]['exitCode'] != 0 or any(matching[0].get(key)!=start.get(key) for key in ('wrapper', 'delegate','class','queryRoot','helper')):
            raise RuntimeError('Helper normal completion mismatch')
        if still_live(start['wrapper']) or still_live(start['delegate']):
            return None
    return {'events': events, 'operations': keys, 'allNormal': True,
            'allExactProcessesGone': True, 'nameExemptions': False,
            'queryEvents':queries,'queryOperations':query_keys,'allQueriesNormal':True,
            'harnessQueries':len(harness)}


if __name__ == '__main__':
    try:
        raise SystemExit(run(sys.argv[1:]))
    except Exception as error:
        print('Exact private helper refused: ' + repr(error), file=sys.stderr)
        raise SystemExit(125)
