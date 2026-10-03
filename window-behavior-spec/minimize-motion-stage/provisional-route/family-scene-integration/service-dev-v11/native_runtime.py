"""Explicit staged native composition. Importing does not create or launch anything."""
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
    def __init__(self,*args,session_guard,core_hash,**kwargs):
        self.session_guard=session_guard;self.core_hash=core_hash
        super().__init__(*args,**kwargs)
    def commit(self,operation,window,preview_ready=False):
        if operation not in ('minimize','restore'):raise ValueError('native commit must be resolved endpoint')
        self.session_guard.verify()
        env=dict(self.session_guard.env,HYPR_WINDOWCTL_FAMILY_SINGLE='1',HYPR_WINDOWCTL_PREVIEW_READY='1' if preview_ready else '0')
        with PinnedExecutable(self.production.CORE,self.core_hash) as executable:
            subprocess.run([executable.path,operation,window['address'],str(window['stableId']),str(window['pid'])],pass_fds=(executable.fd,),env=env,check=True,stdout=subprocess.DEVNULL,timeout=8)

class NativeFactory:
    def __init__(self,root,guard,*,producer,producer_hash,core,core_hash):
        self.root=Path(root);self.guard=guard
        expected=Path(guard.env['XDG_RUNTIME_DIR'])/'hypr-window-motion'
        if self.root.resolve()==expected.resolve() or not self.root.resolve().is_relative_to(expected.resolve()):raise ValueError('native runtime must be below selected private motion root')
        for name in ('XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY'):
            if os.environ.get(name)!=guard.env.get(name):raise ValueError('native adapter process environment differs from selected compositor')
        self.producer=Path(producer);self.producer_hash=producer_hash;self.core=Path(core);self.core_hash=core_hash;self.desktops=[]
        # Material proof now, again on each use. No process/actor constructed here.
        for path,expected in ((producer,producer_hash),(core,core_hash)):
            with PinnedExecutable(path,expected):pass
    def __call__(self,number):
        self.guard.verify();actors=self.root/'actors';actors.mkdir(mode=0o700,exist_ok=True);private_directory(actors)
        desktop=PinnedNativeDesktop(actors/f'actor-{number}-{uuid.uuid4().hex[:8]}',core=self.core,cache_root=self.root/'snapshot-cache',session_guard=self.guard,core_hash=self.core_hash)
        binding=FailureBinding()
        with PinnedExecutable(self.producer,self.producer_hash) as executable:
            transport=PipeTransport(executable.path,env=self.guard.env,failure=binding,pass_fds=(executable.fd,))
        transport.bind_controller=lambda controller:binding.bind(controller.transport_failure)
        self.desktops.append(desktop)
        return desktop,transport
    def context(self,request):
        self.guard.verify()
        if not self.desktops:raise RuntimeError('accepted request actor missing')
        return NativeContextProvider(self.desktops[0],session=self.guard.session)(request)

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
    service=RuntimeService(args.root,args.session,factory,factory.context)
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
