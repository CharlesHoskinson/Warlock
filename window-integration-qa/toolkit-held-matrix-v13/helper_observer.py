#!/usr/bin/python3
"""Exact private compositor helper supervisor. Imports have no side effects."""
from pathlib import Path
import fcntl
import errno
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
    except (FileNotFoundError, ProcessLookupError) as error:
        if error.errno not in (errno.ENOENT, errno.ESRCH):raise
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
    candidates=[(kind,row) for kind,row in config['queryRoots'].items() if kind in ('qs','harness') and taskbar['parent']==row['identity']['pid']]
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

def service_ancestor(wrapper,config):
    row=config['queryRoots']['service'];root=process(row['identity']['pid'])
    if wrapper['parent']!=root['pid'] or any(root[k]!=row['identity'][k] for k in ('pid','start','pgid')):raise RuntimeError('Service query root lifetime changed')
    executable=(Path('/proc')/str(root['pid'])/'exe').resolve()
    if executable!=Path(row['executable']).resolve() or digest(executable)!=row['executableSHA256'] or cmdline(root['pid'])!=row['argv']:
        raise RuntimeError('Service query root executable/argv changed')
    query_environment(root['pid'],config)
    if (Path('/proc')/str(root['pid'])/'cgroup').read_text().strip()!=Path('/proc/self/cgroup').read_text().strip():raise RuntimeError('Service query root scope changed')
    return [root]

def service_member(row):
    if (not isinstance(row,dict) or set(row)!=set(('address','stableId','pid'))
        or not isinstance(row['address'],str) or not re.fullmatch(r'0x[0-9a-f]{1,16}',row['address'])
        or not isinstance(row['stableId'],str) or not re.fullmatch(r'[0-9a-f]{1,16}',row['stableId'])
        or type(row['pid']) is not int or not 1<=row['pid']<(1<<31)):
        raise RuntimeError('Exact pinned service member required')
    return row['address']+':'+row['stableId']+':'+str(row['pid'])

def service_operation(args,config):
    sources=config['queryRoots']['service']
    for path,expected in {sources['source']:sources['sourceSHA256'],**sources['sources']}.items():
        if digest(path)!=expected:raise RuntimeError('Exact service query source changed')
    if len(args)!=3 or args[0]!='hoskinson.windows':raise RuntimeError('Unknown service helper query')
    if args[1]=='motionRefresh' and args[2]=='{}':return 'service-motionRefresh',config['serviceRefreshLimit']
    if args[1]!='motionTarget':raise RuntimeError('Unknown service helper method/payload')
    def unique_pairs(pairs):
        result={}
        for key,value in pairs:
            if key in result:raise RuntimeError('Duplicate service JSON key')
            result[key]=value
        return result
    if len(args[2])>4096:raise RuntimeError('Bounded service identity JSON required')
    try:member=json.loads(args[2],object_pairs_hook=unique_pairs,parse_constant=lambda value:(_ for _ in ()).throw(RuntimeError('Nonfinite service JSON')))
    except ValueError as error:raise RuntimeError('Malformed service identity JSON') from error
    token=service_member(member)
    if member not in config['serviceMembers'] or args[2]!=json.dumps(member):raise RuntimeError('Service member/payload differs from exact production identity')
    return 'service-motionTarget:'+token,config['serviceTargetLimitPerMember']


EVALUATION_RULES = {'initial': (1, 1), 'reload': (1, 1), 'native-load': (2, 2),
                    'native-unload': (1, 0), 'probe-unload': (1, 0)}


def material_witness(path, limit=134217728):
    path=Path(path)
    if not path.is_absolute() or path != path.resolve():raise RuntimeError('Canonical evaluation material path required')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    with os.fdopen(fd,'rb') as stream:
        before=os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_uid!=os.getuid() or before.st_mode&0o022 or before.st_size>limit:
            raise RuntimeError('Unsafe evaluation material')
        data=stream.read(limit+1);after=os.fstat(stream.fileno());named=path.lstat()
    identity=lambda row:[row.st_dev,row.st_ino,row.st_uid,row.st_mode,row.st_size,row.st_mtime_ns,row.st_ctime_ns]
    if len(data)!=before.st_size or identity(before)!=identity(after) or identity(before)!=identity(named):
        raise RuntimeError('Evaluation material changed across complete EOF')
    return dict(path=str(path),sha256=digest_bytes(data),identity=identity(before),completeEOF=True)


def evaluation_keys(ticket):
    kind=ticket.get('kind');serial=ticket.get('serial');nonce=ticket.get('nonce')
    if kind not in EVALUATION_RULES or type(serial) is not int or not 1<=serial<=100 or not isinstance(nonce,str) or not re.fullmatch('[0-9a-f]{32}',nonce):
        raise RuntimeError('Exact bounded evaluation ticket required')
    count,relay=EVALUATION_RULES[kind]
    if type(ticket.get('count')) is not int or type(ticket.get('relayOrdinal')) is not int or (ticket['count'],ticket['relayOrdinal'])!=(count,relay):
        raise RuntimeError('Evaluation ticket differs from source-backed command obligations')
    prefix='evaluation:'+str(serial)+':'+nonce+':'
    return [prefix+str(index)+':hydrate' for index in range(1,count+1)]+([prefix+str(relay)+':inactive-fileDrag'] if relay else [])


def evaluation_operation(config,environment,base):
    nonce=environment.get('WINDOW_QA_EVALUATION_NONCE');ordinal=environment.get('WINDOW_QA_EVALUATION_ORDINAL')
    if not isinstance(nonce,str) or not re.fullmatch('[0-9a-f]{32}',nonce) or not isinstance(ordinal,str) or not re.fullmatch('[1-9][0-9]?',ordinal):
        raise RuntimeError('Actual child evaluation ticket/ordinal absent or malformed')
    candidates=[ticket for ticket in config['evaluationTickets'] if ticket.get('nonce')==nonce]
    if len(candidates)!=1 or config.get('activeEvaluation')!=nonce:raise RuntimeError('Actual child evaluation not uniquely armed')
    ticket=candidates[0];keys=evaluation_keys(ticket)
    if config['evaluationTickets'].index(ticket)+1!=ticket['serial'] or len(config['evaluationTickets'])>100:raise RuntimeError('Exact sequential occurrence ticket required')
    if ticket['kind']=='initial':
        if ticket.get('command')!=config['evaluationInitialCommand']:raise RuntimeError('Initial exact paired evaluation command changed')
    elif ticket['kind']=='reload':
        if ticket.get('command')!=['reload'] or ticket.get('artifact') is not None:raise RuntimeError('Exact explicit reload command required')
    else:
        action='load' if ticket['kind']=='native-load' else 'unload'
        if not isinstance(ticket.get('artifact'),dict) or ticket.get('command')!=['plugin',action,ticket['artifact']['path']] or ticket['artifact']!=config['evaluationArtifacts']['probe' if ticket['kind']=='probe-unload' else 'native']:raise RuntimeError('Exact pinned artifact command required')
    if environment.get('WINDOW_QA_EVALUATION_KIND')!=ticket['kind'] or environment.get('WINDOW_QA_EVALUATION_LIMIT')!=str(ticket['count']) or int(ordinal)>ticket['count']:
        raise RuntimeError('Actual child evaluation command/occurrence differs')
    if ticket['compositor']!=config['compositor'] or ticket['instance']!=config['instance']:
        raise RuntimeError('Evaluation selected compositor lifetime changed')
    root=ticket['root']
    if root!=config['queryRoots']['harness'] or process(root['identity']['pid'])!=root['identity']:
        raise RuntimeError('Evaluation harness exact lifetime changed')
    executable=(Path('/proc')/str(root['identity']['pid'])/'exe').resolve()
    if cmdline(root['identity']['pid'])!=root['argv'] or executable!=Path(root['executable']).resolve() or digest(executable)!=root['executableSHA256'] or digest(root['source'])!=root['sourceSHA256']:
        raise RuntimeError('Evaluation harness source/executable/argv changed')
    if (Path('/proc')/str(root['identity']['pid'])/'cgroup').read_text()!=Path('/proc/self/cgroup').read_text():
        raise RuntimeError('Evaluation harness scope changed')
    proof=ticket['armIPC']
    if proof.get('completeServerEOF') is not True or proof.get('replySHA256')!=config['versionSHA256'] or proof.get('socketIdentity')!=config['socketIdentity'] or proof.get('peer',{}).get('pid')!=config['compositor']['pid']:
        raise RuntimeError('Evaluation arming transport witness differs')
    if ticket['configuration']!=config['evaluationConfiguration'] or material_witness(ticket['configuration']['path'])!=ticket['configuration']:
        raise RuntimeError('Immutable startup configuration changed')
    if ticket.get('artifact') is not None and material_witness(ticket['artifact']['path'])!=ticket['artifact']:
        raise RuntimeError('Evaluation command artifact changed')
    key='evaluation:'+str(ticket['serial'])+':'+nonce+':'+ordinal+':'+base
    if key not in keys:raise RuntimeError('Callback outside actual evaluation context lifetime')
    return key


def load_delegate_diagnostic(config,wrapper,ancestry):
    """Exact private evidence source only after the original query authorization."""
    import types
    settings=config['delegateDiagnostic'];path=Path(settings['source']);home=Path(config['log']).parent
    if path!=home/'.local/bin/delegate_diagnostics.py' or Path(settings['directory'])!=home/'delegate-diagnostics':raise RuntimeError('Exact private diagnostic paths required')
    regular(path,0o700);witness=material_witness(path,131072);data=path.read_bytes()
    if len(data)>131072 or witness!=material_witness(path,131072) or witness['sha256']!=settings['sourceSHA256'] or digest_bytes(data)!=settings['sourceSHA256']:raise RuntimeError('Exact reviewed observer bytes changed')
    module=types.ModuleType('_owned_delegate_diagnostics');module.__file__=str(path);exec(compile(data,str(path),'exec'),module.__dict__)
    parent=ancestry[0];qs=ancestry[1]
    if wrapper['parent']!=parent['pid'] or any(qs[k]!=config['queryRoots']['qs']['identity'][k] for k in ('pid','start','pgid')):raise RuntimeError('Exact diagnostic snapshot/QS lineage required')
    actual=Path(config['actual'])
    if not actual.read_bytes().startswith(b'#!/usr/bin/env python3\n'):raise RuntimeError('Exact actual backend interpreter chain required')
    executable=Path('/usr/bin/python3').resolve();env_executable=Path('/usr/bin/env').resolve()
    chain=[dict(executable=str(env_executable),executableSHA256=digest(env_executable),argv=['/usr/bin/env','python3',str(actual),'list','--json']),dict(executable=str(executable),executableSHA256=digest(executable),argv=['python3',str(actual),'list','--json'])]
    journal=module.Journal(Path(settings['directory'])/(str(wrapper['pid'])+'-'+str(wrapper['start'])+'.jsonl'))
    return module,journal,parent,qs,chain


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
    service_root=shared.get('queryRoots',{}).get('service')
    service_query=service_root is not None and wrapper['parent']==service_root['identity']['pid']
    query_kind=None
    if service_query:
        query_kind='service';ancestry=service_ancestor(wrapper,config)
    elif query:
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
        if service_query:
            if kind!='shell':raise RuntimeError('No registered service Snap query in exact source baseline')
            prefix,limit=service_operation(args,config);query=True
        else:
            key=('harness-list-json' if query_kind=='harness' else 'list-json:'+str(wrapper['pid'])+':'+wrapper['start']) if query else operation(args)
            if not query:
                if (kind=='shell')!=(key=='inactive-fileDrag'):raise RuntimeError('Operation belongs to another exact helper')
                if key in ('hydrate','inactive-fileDrag'):
                    if 'evaluationTickets' in config:
                        key=evaluation_operation(config,os.environ,key)
                    else:
                        generation=config['loadGeneration']
                        if type(generation) is not int or not 1<=generation<=100:raise RuntimeError('Exact bounded full Snap load generation required')
                        key='generation:'+str(generation)+':'+key
    except RuntimeError as error:
        with locked_log(config['log']) as stream:
            append(stream,{'event':'refused','args':args,'helper':kind,'wrapper':wrapper,'ancestry':ancestry,'ipc':proof,'reason':str(error),'stderr':'Exact private helper refused: '+repr(error)+'\n','exitCode':125,'delegateExecuted':False,'timeNs':time.time_ns()})
        raise
    # Reserve under the existing log lock. No rejected call executes the backend.
    read_fd, write_fd = os.pipe2(os.O_CLOEXEC)
    child = None
    diagnostic=None;diagnostic_journal=None;diagnostic_observer=None;diagnostic_summary=None
    try:
        if query_kind=='qs' and kind=='snap':diagnostic,diagnostic_journal,diagnostic_parent,diagnostic_qs,diagnostic_chain=load_delegate_diagnostic(config,wrapper,ancestry)
        with locked_log(config['log']) as stream:
            old = rows(stream)
            if service_query:
                count=sum(row['event']=='started' and row.get('serviceOperation')==prefix for row in old)
                if count>=limit:
                    error=RuntimeError('Exact service query count exhausted')
                    append(stream,{'event':'refused','args':args,'helper':kind,'wrapper':wrapper,'ancestry':ancestry,'ipc':proof,'reason':str(error),'stderr':'Exact private helper refused: '+repr(error)+'\n','exitCode':125,'delegateExecuted':False,'timeNs':time.time_ns()})
                    raise error
                key=prefix+':'+str(count+1)
            if (not query and key not in config['allowed']) or any(row.get('operation') == key for row in old):
                error=RuntimeError('Duplicate or unauthorized helper operation')
                append(stream, {'event': 'refused', 'operation': key, 'args': args,
                                'helper':kind, 'wrapper': wrapper, 'ancestry': ancestry,
                                'reason':str(error),'stderr':'Exact private helper refused: '+repr(error)+'\n','exitCode':125,'delegateExecuted':False, 'timeNs': time.time_ns()})
                raise error
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
                    if not query and 'evaluationTickets' in config and operation(args) in ('hydrate','inactive-fileDrag'):
                        if evaluation_operation(read_config(config_path),os.environ,operation(args))!=key:os._exit(126)
                    if service_query:
                        service_ancestor(wrapper,config)
                        if service_operation(args,config)!=(prefix,limit):os._exit(126)
                    if diagnostic is not None:
                        regular(config['delegateDiagnostic']['source'],0o700)
                        if digest(config['delegateDiagnostic']['source'])!=config['delegateDiagnostic']['sourceSHA256']:os._exit(126)
                        diagnostic.child_bootstrap()
                    os.execv(config['actual'], [config['actual'], *args])
                except BaseException:
                    os._exit(126)
            os.close(read_fd); read_fd = -1
            delegate = process(child)
            if diagnostic is not None:diagnostic_observer=diagnostic.Observer(diagnostic_journal,delegate,diagnostic_parent,diagnostic_qs,diagnostic_chain,dict(operation=key,args=args,wrapper=wrapper,actual=config['actual'],actualSHA256=config['actualSHA256'],observerSHA256=config['delegateDiagnostic']['sourceSHA256'],sourceGuardBeforeGate=True))
            append(stream, {'event': 'started', 'operation': key, 'args': args,
                            'serviceOperation':prefix if service_query else None,
                            'class':'query' if query else 'compositor','queryRoot':query_kind,'helper':kind, 'wrapper': wrapper, 'delegate': delegate,
                            'ancestry': ancestry, 'ipc': proof, 'scope': scope,
                            'actual': config['actual'], 'actualSHA256': config['actualSHA256'],
                            'diagnosticLog':str(diagnostic_journal.path) if diagnostic_journal is not None else None,
                            'evaluationEnvironment':{name:os.environ.get(name) for name in ('WINDOW_QA_EVALUATION_NONCE','WINDOW_QA_EVALUATION_KIND','WINDOW_QA_EVALUATION_LIMIT','WINDOW_QA_EVALUATION_ORDINAL')} if not query and 'evaluationTickets' in config and operation(args) in ('hydrate','inactive-fileDrag') else None,
                            'timeNs': time.time_ns()})
        os.write(write_fd, b'1'); os.close(write_fd); write_fd = -1
        if diagnostic_observer is not None:status,diagnostic_summary=diagnostic_observer.run()
        else:_, status = os.waitpid(child, 0)
        code = os.waitstatus_to_exitcode(status)
        with locked_log(config['log']) as stream:
            append(stream, {'event': 'terminal', 'operation': key,
                            'serviceOperation':prefix if service_query else None,
                            'class':'query' if query else 'compositor','queryRoot':query_kind,'helper':kind, 'wrapper': wrapper, 'delegate': delegate,
                            'exitCode': code, 'timeNs': time.time_ns(),
                            'diagnostic':diagnostic_summary})
        if code < 0:
            signal.signal(-code, signal.SIG_DFL)
            os.kill(os.getpid(), -code)
        return code
    finally:
        if diagnostic_journal is not None:diagnostic_journal.close()
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


def summarize(events, allowed, require_all=True,expect_harness=False,expected_service=None):
    starts = [row for row in events if row['event'] == 'started']
    terminals = [row for row in events if row['event'] == 'terminal']
    if len(events) != len(starts) + len(terminals):
        raise RuntimeError('Unknown helper event')
    comp=[row for row in starts if row.get('class','compositor')=='compositor']
    queries=[row for row in starts if row.get('class')=='query']
    if len(comp)+len(queries)!=len(starts):raise RuntimeError('Unknown helper authority class')
    keys = [row['operation'] for row in comp]
    query_keys=[row['operation'] for row in queries]
    if len(query_keys)!=len(set(query_keys)) or any(row.get('queryRoot') not in ('qs','harness','service') for row in queries):raise RuntimeError('Duplicate/unknown query role')
    service=[row for row in queries if row.get('queryRoot')=='service']
    if expected_service is not None:
        actual={prefix:sum(row.get('serviceOperation')==prefix for row in service) for prefix in expected_service}
        if any(row.get('serviceOperation') not in expected_service for row in service):raise RuntimeError('Unregistered service operation')
        if actual!=expected_service:raise RuntimeError('Incomplete/extra service helper queries')
    harness=[row for row in queries if row.get('queryRoot')=='harness']
    if len(harness)>1 or (expect_harness and len(harness)!=1):raise RuntimeError('Exactly one harness query required')
    if len(keys) != len(set(keys)) or not set(keys).issubset(allowed) or (require_all and set(keys) != set(allowed)):
        raise RuntimeError('Missing/duplicate/unregistered helper operation')
    if len(terminals) != len(starts):
        return None
    for start in starts:
        matching = [row for row in terminals if row['operation'] == start['operation']]
        if len(matching) != 1 or matching[0]['exitCode'] != 0 or any(matching[0].get(key)!=start.get(key) for key in ('wrapper', 'delegate','class','queryRoot','helper','serviceOperation')):
            raise RuntimeError('Helper normal completion mismatch')
        if still_live(start['wrapper']) or still_live(start['delegate']):
            return None
    return {'events': events, 'operations': keys, 'allNormal': True,
            'allExactProcessesGone': True, 'nameExemptions': False,
            'queryEvents':queries,'queryOperations':query_keys,'allQueriesNormal':True,
            'harnessQueries':len(harness),'serviceQueries':len(service)}


if __name__ == '__main__':
    try:
        raise SystemExit(run(sys.argv[1:]))
    except Exception as error:
        print('Exact private helper refused: ' + repr(error), file=sys.stderr)
        raise SystemExit(125)
