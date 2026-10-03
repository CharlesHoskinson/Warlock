"""Explicit staged native composition. Importing does not create or launch anything."""
from copy import deepcopy
import argparse
import hashlib
import fcntl
import json
import os
from pathlib import Path
import re
import socket
import stat
import struct
import subprocess
import signal
import sys
import threading
import uuid
import time
from native_desktop import NativeDesktop
from pipe_transport import PipeTransport
from context_provider import NativeContextProvider
from service_runtime import RuntimeService, private_directory, process_start, stop_runtime

class PinnedExecutable:
    def __init__(self,path,expected):
        if re.fullmatch(r'[0-9a-f]{64}',expected or '') is None:raise ValueError('explicit exact executable SHA256 required')
        source=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC);self.fd=None
        try:
            before=os.fstat(source)
            if not stat.S_ISREG(before.st_mode) or before.st_uid!=os.getuid() or not before.st_mode&0o100 or before.st_mode&0o022 or before.st_size>128*1024*1024:raise ValueError('unsafe executable material')
            flags=os.MFD_CLOEXEC|os.MFD_ALLOW_SEALING|getattr(os,'MFD_EXEC',0)
            self.fd=os.memfd_create('motion-pinned-executable',flags);digest=hashlib.sha256()
            while chunk:=os.read(source,1048576):
                digest.update(chunk);written=0
                while written<len(chunk):written+=os.write(self.fd,chunk[written:])
            after=os.fstat(source)
            if (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns) or digest.hexdigest()!=expected:raise ValueError('executable material changed or exact digest differs')
            os.fchmod(self.fd,0o500)
            seals=fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL
            fcntl.fcntl(self.fd,fcntl.F_ADD_SEALS,seals)
            if fcntl.fcntl(self.fd,fcntl.F_GET_SEALS)&seals!=seals:raise ValueError('executable snapshot sealing unavailable')
            os.lseek(self.fd,0,os.SEEK_SET);self.identity=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
        except Exception:self.close();raise
        finally:os.close(source)
    @property
    def path(self):return f'/proc/self/fd/{self.fd}'
    def close(self):
        if getattr(self,'fd',None) is not None:os.close(self.fd);self.fd=None
    def __enter__(self):return self
    def __exit__(self,*args):self.close()

def sanitize_environment(env):return {k:v for k,v in env.items() if not k.startswith('HYPR_WINDOWCTL_')}

class NativeSession:
    def __init__(self,session,pid,start,display,env):
        if (re.fullmatch(r'[A-Za-z0-9_.-]{1,180}',session or '') is None or pid<1 or start<1
                or env.get('HYPRLAND_INSTANCE_SIGNATURE')!=session or env.get('WAYLAND_DISPLAY')!=display):raise ValueError('selected exact compositor/environment required')
        self.session=session;self.pid=pid;self.start=start;self.env=sanitize_environment(env)
        root=Path(env['XDG_RUNTIME_DIR']);private_directory(root)
        wayland=Path(display)
        if not wayland.is_absolute():wayland=root/wayland
        if not wayland.resolve().is_relative_to(root.resolve()):raise ValueError('Wayland socket outside selected private runtime')
        self.sockets=(root/'hypr'/session/'.socket.sock',wayland)
        self.verify()
    def verify(self):
        if process_start(self.pid)!=self.start:raise ValueError('compositor closed or PID reused')
        for index,path in enumerate(self.sockets):
            runtime=Path(self.env['XDG_RUNTIME_DIR'])
            if path.resolve()!=path.absolute() or not path.resolve().is_relative_to(runtime.resolve()):raise ValueError('selected socket path leaves private nonsymlink runtime')
            before=path.lstat()
            if not stat.S_ISSOCK(before.st_mode) or before.st_uid!=os.getuid():raise ValueError('selected compositor socket identity unavailable')
            with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as connection:
                connection.settimeout(.5);connection.connect(str(path))
                pid,uid,_=struct.unpack('3i',connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
                after=path.lstat()
                if pid!=self.pid or uid!=os.getuid() or (before.st_dev,before.st_ino)!=(after.st_dev,after.st_ino):raise ValueError('connected socket is not selected exact compositor')
                if index==0:
                    deadline=time.monotonic()+.5;connection.sendall(b'j/version');reply=bytearray()
                    while True:
                        remaining=deadline-time.monotonic()
                        if remaining<=0:raise TimeoutError('compositor IPC full reply deadline')
                        connection.settimeout(remaining);chunk=connection.recv(4096)
                        if not chunk:break
                        reply.extend(chunk)
                        if len(reply)>65536:raise ValueError('compositor IPC version reply exceeds bound')
                    version=json.loads(reply.decode('utf-8'))
                    if not isinstance(version,dict) or not version or 'error' in version:raise ValueError('compositor IPC version reply invalid/error')
                    after=path.lstat()
                    if (before.st_dev,before.st_ino)!=(after.st_dev,after.st_ino) or process_start(self.pid)!=self.start:raise ValueError('compositor IPC identity changed after complete reply')
                    self.ipc_observation={'request':'j/version','replyBytes':len(reply),'replySHA256':hashlib.sha256(reply).hexdigest(),'completeServerEOF':True,'version':version,'pid':pid,'start':self.start,'socket':[before.st_dev,before.st_ino]}
        if process_start(self.pid)!=self.start:raise ValueError('compositor PID/start changed while connecting')

class FailureBinding:
    def __init__(self):self.lock=threading.Lock();self.callback=None;self.reason=None;self.delivered=False
    def __call__(self,reason):
        with self.lock:
            if self.reason is None:self.reason=reason
            self.deliver()
    def bind(self,callback):
        with self.lock:
            if self.callback is not None:raise RuntimeError('failure sink already bound')
            self.callback=callback;self.deliver()
    def deliver(self):
        if self.callback and self.reason is not None and not self.delivered:
            self.delivered=True
            threading.Thread(target=self.callback,args=(self.reason,),daemon=True).start()

class PinnedNativeDesktop(NativeDesktop):
    def __init__(self,*args,session_guard,core_hash,retirement_guard,retirement_lock,**kwargs):
        if not callable(retirement_guard):raise ValueError('actual actor disposal authority guard required')
        self.session_guard=session_guard;self.core_hash=core_hash
        self.retirement_guard=retirement_guard;self.retirement_lock=retirement_lock
        super().__init__(*args,**kwargs)
    def release_sources(self,sources):
        with self.retirement_lock:
            self.retirement_guard()
            return super().release_sources(sources)
    def dispose(self):
        with self.retirement_lock:
            self.retirement_guard()
            return super().dispose()
    def retire_gestures(self,members):
        self.session_guard.verify()
        result=super().retire_gestures(members,env=self.session_guard.env)
        self.session_guard.verify()
        return result
    def plan_destination(self,window):
        self.session_guard.verify()
        result=super().plan_destination(window)
        self.session_guard.verify()
        return result
    def apply_destination(self,window,plan):
        self.session_guard.verify()
        result=super().apply_destination(window,plan)
        self.session_guard.verify()
        return result
    def refresh_destination(self,window,plan):
        self.session_guard.verify()
        result=super().refresh_destination(window,plan)
        self.session_guard.verify()
        return result
    def commit(self,operation,window,preview_ready=False):
        if operation not in ('minimize','restore'):raise ValueError('native commit must be resolved endpoint')
        self.session_guard.verify()
        env=dict(self.session_guard.env,HYPR_WINDOWCTL_FAMILY_SINGLE='1',HYPR_WINDOWCTL_PREVIEW_READY='1' if preview_ready else '0')
        with PinnedExecutable(self.production.CORE,self.core_hash) as executable:
            self.commands.run([executable.path,operation,window['address'],str(window['stableId']),str(window['pid'])],pass_fds=(executable.fd,),env=env,check=True,stdout=subprocess.DEVNULL,timeout=8)

class NativeFactory:
    def __init__(self,root,guard,*,producer,producer_hash,core,core_hash):
        self.root=Path(root);self.guard=guard
        expected=Path(guard.env['XDG_RUNTIME_DIR'])/'hypr-window-motion'
        if self.root.resolve()==expected.resolve() or not self.root.resolve().is_relative_to(expected.resolve()):raise ValueError('native runtime must be below selected private motion root')
        for name in ('XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY'):
            if os.environ.get(name)!=guard.env.get(name):raise ValueError('native adapter process environment differs from selected compositor')
        self.producer=Path(producer);self.producer_hash=producer_hash;self.core=Path(core);self.core_hash=core_hash;self.desktops=[];self.shared_cache=None
        self.resources={};self.resource_writer=None;self.helper_ownership=None;self.keeper=None;self.journal_lock=None;self.lease_verify=None;self.readonly=None;self.readonly_ownership=None;self.actor_ownership=None
        # Material proof now, again on each use. No process/actor constructed here.
        for path,expected in ((producer,producer_hash),(core,core_hash)):
            with PinnedExecutable(path,expected):pass
    def bind_lease(self,verify):self.lease_verify=verify
    def bind_journal(self,writer):
        self.resource_writer=writer;self.journal_lock=writer.__self__.manager.lock
        from helper_supervisor import Keeper
        self.keeper=Keeper(self.root,self.guard.env,self.helper_changed,reservation_lock=self.journal_lock,actor_record=self.actor_changed)
        try:
            self.keeper.actor_publish()
            if type(self.guard) is NativeSession:
                from readonly_ipc import ReadonlyIPC
                self.readonly=ReadonlyIPC(self.root,self.guard,self.lease_verify,self.readonly_changed,reservation_lock=self.journal_lock)
        except BaseException as error:
            # No actor can be launched before this complete initial binding.
            # Close this exact Keeper through its inherited crash mechanism;
            # retain both the original failure and any refused publication.
            try:self.keeper.abort()
            except BaseException as cleanup_error:error.add_note('Keeper startup cleanup: '+str(cleanup_error))
            raise
    def readonly_changed(self,body):
        self.readonly_ownership=body;self.publish_resource()
    def readonly_snapshot(self):return deepcopy(self.readonly_ownership)
    def helper_changed(self,body):
        self.helper_ownership=body;self.publish_resource()
    def helper_snapshot(self):return deepcopy(self.helper_ownership)
    def actor_changed(self,body):
        self.actor_ownership=deepcopy(body);self.publish_resource()
    def actor_snapshot(self):
        # Publication can fail after the callback received a non-faulted row.
        # Observe the Keeper's latched fault and retain its complete inventory.
        return self.keeper.actor_snapshot() if self.keeper is not None else deepcopy(self.actor_ownership)
    def assert_actor_authority(self,actor=None):
        if self.keeper is None:return
        from service_runtime import actor_unresolved
        with self.journal_lock,self.keeper.lock:
            ledger=self.actor_snapshot()
            if not set(self.keeper.jobs)<=set(ledger['jobs']):
                raise RuntimeError('actor ledger inventory incomplete; source disposal refused')
            if actor is not None:
                if type(actor) is not int or actor<1:raise ValueError('exact actor disposal identity required')
                if any(not isinstance(row,dict) or row.get('actor') is not None and (type(row.get('actor')) is not int or row['actor']<1) for row in ledger['jobs'].values()):
                    raise RuntimeError('actor ledger has unknown job ownership; source disposal refused')
                ledger['jobs']={job:row for job,row in ledger['jobs'].items() if row['actor'] in (None,actor)}
            if actor_unresolved(ledger,drained=False):
                raise RuntimeError('actor ledger lacks durable native results or complete ownership; source disposal refused')
    def close(self):
        if self.readonly:self.readonly.assert_closed()
        if self.keeper:
            from service_runtime import actor_unresolved
            ledger=self.actor_snapshot()
            if actor_unresolved(ledger) or not set(self.keeper.jobs)<=set(ledger['jobs']):
                if not self.keeper.closed:self.keeper.abort()
                raise RuntimeError('actor ledger incomplete or faulted; normal service closure refused')
            if self.keeper.jobs:
                self.keeper.abort();raise RuntimeError('uncertain helper jobs required crash cleanup; normal service closure refused')
            self.keeper.stop()
    def resource_snapshot(self):
        manager=self.resource_writer.__self__.manager
        required={a.number for a in manager.actors+manager.retiring}
        if self.helper_ownership:required.update(job['actor'] for job in self.helper_ownership['jobs'] if job['actor'] is not None)
        live=[v for n,v in self.resources.items() if v['phase']!='closed' or n in required]
        history=[v for n,v in self.resources.items() if v['phase']=='closed' and n not in required][-32:]
        return deepcopy(live+history)
    def publish_resource(self):
        if self.resource_writer is None:raise RuntimeError('native actor requires durable resource journal before launch')
        self.resource_writer()
    def __call__(self,number):
        if self.lease_verify is None:raise ValueError('actual held runtime lease binding required')
        self.lease_verify();self.guard.verify();actors=self.root/'actors';actors.mkdir(mode=0o700,exist_ok=True);private_directory(actors)
        if self.resource_writer is None:raise RuntimeError('native actor requires durable resource journal before launch')
        name=actors/f'actor-{number}-{uuid.uuid4().hex}'
        parent=actors.stat()
        resource={'actor':number,'phase':'reserved','directory':{'path':str(name),'parentIdentity':[parent.st_dev,parent.st_ino],'identity':None},'renderer':None}
        self.resources[number]=resource;self.publish_resource()
        from owned_commands import OwnedCommands
        commands=OwnedCommands(self.keeper,self.guard.env,number,readonly=self.readonly)
        desktop=transport=None
        try:
            desktop=PinnedNativeDesktop(name,core=self.core,cache_root=self.root/'snapshot-cache',session_guard=self.guard,core_hash=self.core_hash,commands=commands,retirement_guard=lambda:self.assert_actor_authority(number),retirement_lock=self.journal_lock)
            resource['directory']['identity']=list(desktop.directory_identity);resource['phase']='directory';self.publish_resource()
            binding=FailureBinding()
            with PinnedExecutable(self.producer,self.producer_hash) as executable:
                def acquired(ownership):
                    resource['renderer']=ownership;resource['phase']='gated';self.publish_resource()
                transport=PipeTransport(executable.path,env=self.guard.env,failure=binding,pass_fds=(executable.fd,),launch_record=acquired,keeper=self.keeper,actor=number)
            resource['phase']='launched';self.publish_resource()
            transport.bind_controller=lambda controller:binding.bind(controller.transport_failure)
            self.desktops.append(desktop)
            self.shared_cache=desktop.shared_cache
            return desktop,transport
        except BaseException:
            from recovery_resources import process_start as owned_start
            stopped=resource['renderer'] is None or owned_start(resource['renderer']['pid'])!=resource['renderer']['start']
            if transport is not None:
                try:transport.close();stopped=True
                except Exception:pass
            if desktop is not None and stopped:
                try:desktop.dispose()
                except Exception:pass
            raise
    def context(self,request):
        self.guard.verify()
        if not self.desktops:raise RuntimeError('accepted request actor missing')
        return NativeContextProvider(self.desktops[0],session=self.guard.session)(request)
    def retired(self,number,desktop):
        with self.journal_lock:
            from recovery_resources import process_start as resource_start
            record=self.resources[number]
            if record['renderer'] and resource_start(record['renderer']['pid'])==record['renderer']['start']:
                raise RuntimeError('actor renderer lifetime still exists after normal retirement')
            if Path(record['directory']['path']).exists():raise RuntimeError('actor directory still exists after normal retirement')
            record['phase']='closed';record['outcome']={'oldLifetimeGone':True,'directoryGone':True,'normalRetirement':True}
            self.publish_resource();self.desktops.remove(desktop)
    def recover(self,previous):
        from recovery_runtime import NativeRecovery
        return NativeRecovery(self,lease_verify=self.lease_verify).recover(previous)
    def housekeep(self):
        if self.shared_cache is None:return
        self.guard.verify()
        from owned_commands import OwnedCommands
        commands=getattr(self,'housekeeping_commands',None) or OwnedCommands(self.keeper,self.guard.env,readonly=self.readonly)
        def clients():return json.loads(commands.check_output(['hyprctl','clients','-j'],env=self.guard.env,text=True,timeout=.6))
        before=clients()
        native=json.loads(commands.check_output(['hyprctl','repl','print(hl.plugin.hyprbars.window_families())'],env=self.guard.env,text=True,timeout=.6))
        after=clients();live=complete_live_identities(before,native,after)
        self.guard.verify()
        self.shared_cache.prune(live,complete=True,nonblocking=True)

def complete_live_identities(before,native,after):
    def check(records):
        if not isinstance(records,list):raise ValueError('complete client/native list required')
        result={};mapped=set()
        for w in records:
            if (not isinstance(w,dict) or not isinstance(w.get('address'),str)
                    or re.fullmatch(r'0x[0-9a-f]{1,16}',w['address']) is None
                    or re.fullmatch(r'[0-9a-f]{1,16}',str(w.get('stableId',''))) is None
                    or not isinstance(w.get('pid'),int) or isinstance(w['pid'],bool) or w['pid']<1
                    or 'mapped' in w and not isinstance(w['mapped'],bool)):
                raise ValueError('invalid complete live identity')
            identity=(w['address'],str(w['stableId']),w['pid'])
            if w['address'] in result:raise ValueError('duplicate complete live address')
            result[w['address']]=identity
            if w.get('mapped',True):mapped.add(identity)
        return set(result.values()),mapped
    b,bm=check(before);n,nm=check(native);a,am=check(after)
    if b!=a or bm!=am or am!=n or n!=nm:raise ValueError('client/native complete identity coverage changed')
    return a

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',required=True);parser.add_argument('--session',required=True);parser.add_argument('--stop',action='store_true');parser.add_argument('--request-stdin',action='store_true')
    parser.add_argument('--pid',type=int);parser.add_argument('--start',type=int);parser.add_argument('--display');parser.add_argument('--producer');parser.add_argument('--producer-sha256');parser.add_argument('--core');parser.add_argument('--core-sha256');args=parser.parse_args()
    if args.stop and args.request_stdin:parser.error('choose one client operation')
    if args.stop:print(json.dumps(stop_runtime(args.root,args.session)));return
    if args.request_stdin:
        data=sys.stdin.buffer.read(8193)
        if len(data)>8192:parser.error('request exceeds bound')
        result=request_runtime(args.root,args.session,json.loads(data));print(json.dumps(result));return
    if any(v is None for v in (args.pid,args.start,args.display,args.producer,args.producer_sha256,args.core,args.core_sha256)):parser.error('explicit daemon requires complete selected session and pinned materials')
    guard=NativeSession(args.session,args.pid,args.start,args.display,dict(os.environ))
    # Native adapter/core uses this process environment. Strip request flags once,
    # before constructing any actor; request single flag remains payload-owned.
    for name in list(os.environ):
        if name.startswith('HYPR_WINDOWCTL_'):del os.environ[name]
    factory=NativeFactory(args.root,guard,producer=args.producer,producer_hash=args.producer_sha256,core=args.core,core_hash=args.core_sha256)
    service=RuntimeService(args.root,args.session,factory,factory.context,recovery=factory.recover)
    signal.signal(signal.SIGTERM,lambda *_:service.stop_requested.set())
    signal.signal(signal.SIGINT,lambda *_:service.stop_requested.set())
    service.run()

class UncertainAcceptance(RuntimeError):
    acceptance_unknown=True

def request_runtime(root,session,request,*,timeout=2):
    """One verified API send. Never starts an actor or falls back/retries."""
    from service_runtime import read_private
    root=private_directory(root);api=root/'api.sock';owner=read_private(root/'owner.json');before=api.lstat()
    if (not stat.S_ISSOCK(before.st_mode) or before.st_uid!=os.getuid() or before.st_mode&0o077
            or owner.get('session')!=session or owner.get('socket')!=[before.st_dev,before.st_ino]
            or process_start(owner.get('pid',0))!=owner.get('start')):raise ValueError('runtime/session/socket owner not exact live identity')
    encoded=json.dumps(request,allow_nan=False,separators=(',',':')).encode()+b'\n'
    if len(encoded)>8192:raise ValueError('API request exceeds bound')
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as connection:
        connection.settimeout(timeout);connection.connect(str(api))
        pid,uid,_=struct.unpack('3i',connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12));after=api.lstat()
        if pid!=owner['pid'] or uid!=os.getuid() or (after.st_dev,after.st_ino)!=(before.st_dev,before.st_ino) or process_start(pid)!=owner['start']:raise ValueError('connected API peer changed')
        sent=False
        try:
            # A partial send is already uncertain; no duplicate native fallback.
            sent=True;connection.sendall(encoded);data=bytearray()
            while b'\n' not in data:
                part=connection.recv(8193-len(data))
                if not part or len(data)+len(part)>8192:raise ValueError('missing/unbounded API response')
                data.extend(part)
            result=json.loads(bytes(data).split(b'\n',1)[0])
            if not isinstance(result,dict) or not isinstance(result.get('ok'),bool):raise ValueError('malformed API acceptance response')
            return result
        except Exception as error:
            if sent:raise UncertainAcceptance('API response unavailable after send; acceptance unknown, no retry/fallback') from error
            raise


if __name__=='__main__':main()
