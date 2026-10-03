"""Exact Linux orphan ownership. Import performs no process or native operation."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import select
import signal
import stat
import subprocess
import sys
import time
from recovery_intent import positive

SEALS=fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL
MAX_MATERIAL=128*1024*1024
HANDOFF=b'''import os,sys\ngate=int(sys.argv[1]);target=int(sys.argv[2]);script=int(sys.argv[3])\npermit=os.read(gate,1);os.close(gate)\nif permit!=b"G":sys.exit(125)\nos.close(script)\nos.execve("/proc/self/fd/"+str(target),["/proc/self/fd/"+str(target)],dict(os.environ))\n'''


def process_start(pid):
    try:return int(Path(f'/proc/{positive(pid)}/stat').read_text().rsplit(') ',1)[1].split()[19])
    except (FileNotFoundError,ProcessLookupError):return None


def renderer_terminal_state(row):
    """Read-only exact lifetime closure; an unreaped PID is not execution."""
    checked_renderer(row)
    pid=row['pid'];expected=row['start']
    def observe():
        try:raw=Path(f'/proc/{pid}/stat').read_text()
        except (FileNotFoundError,ProcessLookupError):return None
        # State and start must come from ONE kernel stat record. Never join
        # independently sampled state/start into a fabricated lifetime.
        head,tail=raw.rsplit(') ',1);fields=tail.split()
        if head.split(' ',1)[0]!=str(pid) or len(fields)<20:
            raise ValueError('complete exact renderer stat required')
        state=fields[0]
        if state not in ('R','S','D','T','t','Z','X','x','K','W','P','I'):
            raise ValueError('unknown renderer execution state; quarantined')
        start=positive(int(fields[19]))
        return {'start':start,'state':state}
    def absent_or_reused(current):
        if current is None:return {'oldLifetimeGone':True,'kind':'absent','observed':None}
        if current['start']!=expected:return {'oldLifetimeGone':True,'kind':'reused','observed':current}
        return None
    current=observe();gone=absent_or_reused(current)
    if gone is not None:return gone
    try:pidfd=os.pidfd_open(pid)
    except ProcessLookupError:return {'oldLifetimeGone':True,'kind':'absent','observed':None}
    try:
        current=observe();gone=absent_or_reused(current)
        if gone is not None:return gone
        poll=select.poll();poll.register(pidfd,select.POLLIN)
        events=poll.poll(0)
        if events and (len(events)!=1 or events[0][0]!=pidfd or not(events[0][1]&select.POLLIN) or events[0][1]&~(select.POLLIN|select.POLLHUP)):
            raise ValueError('unexpected renderer pidfd terminal event; quarantined')
        terminal=bool(events)
        return {'oldLifetimeGone':terminal,'kind':'exited' if terminal else 'running','observed':current}
    finally:os.close(pidfd)


def material_fd(fd,*,sealed=False):
    before=os.fstat(fd)
    if not stat.S_ISREG(before.st_mode) or before.st_mode&0o022 or before.st_size>MAX_MATERIAL:
        raise ValueError('regular bounded immutable executable material required')
    digest=hashlib.sha256();offset=0
    while data:=os.pread(fd,1048576,offset):digest.update(data);offset+=len(data)
    after=os.fstat(fd)
    if (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns) or offset!=before.st_size:
        raise ValueError('executable material changed during ownership read')
    seals=fcntl.fcntl(fd,fcntl.F_GET_SEALS) if sealed else None
    if sealed and seals&SEALS!=SEALS:raise ValueError('complete executable seals required')
    return {'device':before.st_dev,'inode':before.st_ino,'size':before.st_size,'sha256':digest.hexdigest(),'seals':seals}


def material_path(path,*,sealed=False):
    fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC)
    try:return material_fd(fd,sealed=sealed)
    finally:os.close(fd)


def checked_material(row,*,sealed):
    if not isinstance(row,dict) or set(row)!={'device','inode','size','sha256','seals'}:
        raise ValueError('complete executable identity required')
    if any(type(row[k]) is not int or row[k]<0 for k in ('device','inode','size')) or row['inode']<1 or row['size']>MAX_MATERIAL:
        raise ValueError('typed executable identity required')
    if type(row['sha256']) is not str or not re.fullmatch('[0-9a-f]{64}',row['sha256']):raise ValueError('exact material digest required')
    if sealed:
        if type(row['seals']) is not int or row['seals']&SEALS!=SEALS:raise ValueError('typed complete seals required')
    elif row['seals'] is not None:raise ValueError('launcher executable is not a sealed memfd')
    return row


def gated_process(executable,*,env,pass_fds,record,process_factory=subprocess.Popen):
    """Run a sealed handoff child; durable record callback precedes renderer exec."""
    match=re.fullmatch('/proc/self/fd/([0-9]+)',str(executable))
    if match is None:raise ValueError('sealed renderer descriptor launch required')
    target=int(match[1]);producer=material_fd(target,sealed=True)
    if target not in pass_fds:raise ValueError('selected renderer descriptor must be inherited')
    script=os.memfd_create('motion-recovery-handoff',os.MFD_CLOEXEC|os.MFD_ALLOW_SEALING)
    gate_read,gate_write=os.pipe2(os.O_CLOEXEC);child=None
    try:
        os.write(script,HANDOFF);os.fchmod(script,0o400);fcntl.fcntl(script,fcntl.F_ADD_SEALS,SEALS)
        script_material=material_fd(script,sealed=True)
        launcher=str(Path(sys.executable).resolve());launcher_material=material_path(launcher)
        argv=[launcher,f'/proc/self/fd/{script}',str(gate_read),str(target),str(script)]
        child=process_factory(argv,env=env,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1,pass_fds=(*pass_fds,script,gate_read))
        start=process_start(child.pid)
        if start is None:raise ValueError('gated child exited before ownership')
        ownership={'pid':child.pid,'start':positive(start),'uid':os.getuid(),'producer':producer,'launcher':launcher_material,
            'script':script_material,'argv':argv,'scriptFD':script,'producerFD':target,
            'environment':{k:env[k] for k in ('XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY')}}
        # Exact ownership is established while the child remains blocked. This
        # read does not require executing the renderer or connecting Wayland.
        verify_process(ownership)
        record(ownership)
        if os.write(gate_write,b'G')!=1:raise BrokenPipeError('renderer handoff gate failed')
        return child
    except Exception:
        # Gate EOF discharges a child before renderer execution. If the gate
        # already opened, this process is still our exact Popen child.
        os.close(gate_write);gate_write=None
        if child is not None:
            try:child.wait(timeout=2)
            except subprocess.TimeoutExpired:child.kill();child.wait(timeout=2)
            for stream in (child.stdin,child.stdout,child.stderr):
                if stream:stream.close()
        raise
    finally:
        for fd in (script,gate_read,gate_write):
            if fd is not None:os.close(fd)


def checked_renderer(row):
    expected={'pid','start','uid','producer','launcher','script','argv','scriptFD','producerFD','environment'}
    owned={'targetArgv','mode','interpreter','policy','policySHA256'}
    modern=isinstance(row,dict) and set(row)==expected|owned
    if modern:
        from helper_policy import POLICY
        if row['policy']!=POLICY or row['policySHA256']!=hashlib.sha256(Path(__file__).with_name('helper_policy.py').read_bytes()).hexdigest():raise ValueError('exact inherited confinement policy required')
        if row['mode']!='elf' or row['interpreter'] is not None or row['targetArgv']!=[f"/proc/self/fd/{row['producerFD']}"]:raise ValueError('owned renderer must be exact sealed ELF default invocation')
        from owned_launch import handoff_source
        if row['script']['sha256']!=hashlib.sha256(handoff_source()).hexdigest():raise ValueError('reviewed renderer handoff source required')
        expected|=owned
    if not isinstance(row,dict) or set(row)!=expected:raise ValueError('complete durable renderer ownership required')
    positive(row['pid']);positive(row['start'])
    if type(row['uid']) is not int or row['uid']!=os.getuid():raise ValueError('exact renderer UID required')
    checked_material(row['producer'],sealed=True);checked_material(row['launcher'],sealed=False);checked_material(row['script'],sealed=True)
    if any(type(row[k]) is not int or row[k]<0 for k in ('scriptFD','producerFD')):raise ValueError('typed inherited descriptors required')
    if not isinstance(row['argv'],list) or len(row['argv'])!=(8 if modern else 5) or any(type(v) is not str for v in row['argv']):raise ValueError('exact gated argv required')
    if row['argv'][1]!=f"/proc/self/fd/{row['scriptFD']}" or not row['argv'][2].isdigit():raise ValueError('gated argv descriptor binding differs')
    if modern:
        if not row['argv'][3].isdigit() or row['argv'][4]!=str(row['producerFD']) or json.loads(row['argv'][5])!=row['targetArgv'] or row['argv'][6:]!=['elf','-1']:raise ValueError('owned handoff argument binding differs')
    elif row['argv'][3:]!=[str(row['producerFD']),str(row['scriptFD'])]:raise ValueError('gated argv descriptor binding differs')
    if not isinstance(row['environment'],dict) or set(row['environment'])!={'XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY'} or any(type(v) is not str or not v for v in row['environment'].values()):raise ValueError('exact selected renderer environment required')
    return row


def verify_process(row):
    checked_renderer(row);pid=row['pid']
    if process_start(pid)!=row['start']:raise ValueError('exact renderer PID/start changed')
    status=Path(f'/proc/{pid}/status').read_text()
    uid=re.search(r'^Uid:\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)',status,re.M)
    if uid is None or any(int(v)!=row['uid'] for v in uid.groups()):raise ValueError('renderer UID changed')
    raw=Path(f'/proc/{pid}/environ').read_bytes();environment=dict(item.split(b'=',1) for item in raw.split(b'\0') if b'=' in item)
    if any(environment.get(k.encode())!=v.encode() for k,v in row['environment'].items()):raise ValueError('renderer selected environment changed')
    # exe may change once from launcher to renderer. If that happens during the
    # read, refuse this observation; the caller can repeat before any signal.
    exe=Path(f'/proc/{pid}/exe');info=exe.stat();key=(info.st_dev,info.st_ino)
    if key==(row['producer']['device'],row['producer']['inode']):
        actual=material_path(exe,sealed=True)
        if actual!=row['producer']:raise ValueError('sealed renderer executable changed')
        phase='executed'
    elif key==(row['launcher']['device'],row['launcher']['inode']):
        if material_path(exe)!=row['launcher']:raise ValueError('launcher executable changed')
        argv=Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')[:-1]
        if argv!=[v.encode() for v in row['argv']]:raise ValueError('gated launcher argv changed')
        for name,fd in (('script',row['scriptFD']),('producer',row['producerFD'])):
            if material_path(f'/proc/{pid}/fd/{fd}',sealed=True)!=row[name]:raise ValueError('gated inherited material changed')
        phase='gated'
    else:raise ValueError('live old lifetime has unrelated executable; quarantined')
    after=exe.stat()
    if (after.st_dev,after.st_ino)!=key or process_start(pid)!=row['start']:raise ValueError('renderer exec/lifetime changed during ownership observation')
    return phase


def retire_renderer(row,*,expected_environment,timeout=2):
    checked_renderer(row)
    if row['environment']!=expected_environment:raise ValueError('journal renderer belongs to another selected session')
    if process_start(row['pid'])!=row['start']:return {'oldLifetimeGone':True,'signaled':False,'forced':False}
    try:pidfd=os.pidfd_open(row['pid'])
    except ProcessLookupError:return {'oldLifetimeGone':True,'signaled':False,'forced':False}
    try:
        if process_start(row['pid'])!=row['start']:return {'oldLifetimeGone':True,'signaled':False,'forced':False}
        poll=select.poll();poll.register(pidfd,select.POLLIN)
        if poll.poll(0):return {'oldLifetimeGone':True,'signaled':False,'forced':False}
        phase=verify_process(row)
        signal.pidfd_send_signal(pidfd,signal.SIGTERM)
        poll=select.poll();poll.register(pidfd,select.POLLIN)
        forced=not bool(poll.poll(int(timeout*1000)))
        if forced:
            signal.pidfd_send_signal(pidfd,signal.SIGKILL)
            if not poll.poll(int(timeout*1000)):raise RuntimeError('exact orphan lifetime did not exit; no source disposal')
        return {'oldLifetimeGone':True,'signaled':True,'forced':forced,'observedPhase':phase,'crashCleanup':True,'normalShutdown':False}
    finally:os.close(pidfd)


def dispose_directory(row,*,renderer_gone,inspection_only=False):
    if renderer_gone is not True:raise ValueError('renderer lifetime closure required before directory disposal')
    if not isinstance(row,dict) or set(row)!={'path','parentIdentity','identity'}:raise ValueError('complete actor directory ownership required')
    if type(row['path']) is not str:raise ValueError('typed actor path required')
    for value in (row['parentIdentity'],row['identity']):
        if value is None:continue
        if not isinstance(value,list) or len(value)!=2 or any(type(v) is not int or v<0 for v in value) or value[1]<1:raise ValueError('typed actor inode required')
    path=Path(row['path'])
    if path.resolve()!=path.absolute():raise ValueError('nonsymlink actor directory required')
    parent=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
    child=None
    try:
        p=os.fstat(parent)
        if [p.st_dev,p.st_ino]!=row['parentIdentity'] or p.st_uid!=os.getuid() or p.st_mode&0o077:raise ValueError('actor parent changed')
        try:child=os.open(path.name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent)
        except FileNotFoundError:return {'directoryGone':True,'deleted':False}
        info=os.fstat(child)
        if row['identity'] is None:raise ValueError('allocation gap has no durable directory identity; quarantined')
        if [info.st_dev,info.st_ino]!=row['identity'] or info.st_uid!=os.getuid() or info.st_mode&0o077:raise ValueError('actor directory identity/private mode changed')
        epoch=r'[0-9a-f]{12}-[1-9][0-9]{0,14}'
        full=r'full-[0-9a-f]{1,16}-[1-9][0-9]*'
        pattern=re.compile(r'(?:(?:(?:frame|composed)-)?'+epoch+r'\.png|'+full+r'\.(?:png|json)|'+full+'-'+epoch+r'\.(?:png|json)\.tmp)')
        entries={}
        for name in os.listdir(child):
            s=os.stat(name,dir_fd=child,follow_symlinks=False)
            if (not pattern.fullmatch(name) or not stat.S_ISREG(s.st_mode) or s.st_uid!=os.getuid() or s.st_mode&0o077):raise ValueError('unexpected actor material; quarantined')
            entries[name]=(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
        for name,expected in entries.items():
            s=os.stat(name,dir_fd=child,follow_symlinks=False)
            if (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)!=expected:raise ValueError('actor material changed during disposal')
        named=os.stat(path.name,dir_fd=parent,follow_symlinks=False)
        if [named.st_dev,named.st_ino]!=row['identity']:raise ValueError('actor name replaced before disposal')
        if inspection_only:return {'directoryGone':False,'inspected':True,'captureFiles':len(entries)}
        for name in entries:os.unlink(name,dir_fd=child)
        named=os.stat(path.name,dir_fd=parent,follow_symlinks=False)
        if [named.st_dev,named.st_ino]!=row['identity']:raise ValueError('actor name replaced before disposal')
        os.rmdir(path.name,dir_fd=parent);os.fsync(parent)
        return {'directoryGone':True,'deleted':True,'captureFilesDeleted':len(entries)}
    finally:
        if child is not None:os.close(child)
        os.close(parent)
