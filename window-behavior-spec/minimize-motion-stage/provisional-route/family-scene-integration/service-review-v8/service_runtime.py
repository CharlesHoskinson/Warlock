"""Explicit private service lifecycle; import never launches/connects/creates files."""
from dataclasses import asdict
import fcntl
import hashlib
import json
import os
from pathlib import Path
import socket
import stat
import threading
import time
import uuid
from scene_manager import SceneManager
from socket_frontend import SocketFrontend
from scene_controller import key

MAX_BYTES=1048576

def process_start(pid):
    try:return int(Path(f'/proc/{int(pid)}/stat').read_text().rsplit(') ',1)[1].split()[19])
    except (OSError,ValueError,IndexError):return None

def private_directory(path,*,create=False):
    path=Path(path)
    if create:path.mkdir(mode=0o700,exist_ok=True)
    s=path.lstat()
    if not stat.S_ISDIR(s.st_mode) or s.st_uid!=os.getuid() or s.st_mode&0o077 or path.resolve()!=path.absolute():
        raise ValueError('runtime must be a private nonsymlink directory owned by this UID')
    return path

def read_private(path):
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        s=os.fstat(fd)
        if not stat.S_ISREG(s.st_mode) or s.st_uid!=os.getuid() or s.st_mode&0o077 or s.st_size>MAX_BYTES:
            raise ValueError('unsafe/oversized runtime material')
        data=os.read(fd,MAX_BYTES+1);after=os.fstat(fd)
        if (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns) or len(data)!=s.st_size:
            raise ValueError('runtime material changed during read')
        return json.loads(data)
    finally:os.close(fd)

class JournalStore:
    def __init__(self,root,session):
        self.root=private_directory(root);self.path=self.root/'journal.json';self.session=session
    def read(self):
        try:j=read_private(self.path)
        except FileNotFoundError:return None
        body=j['body']
        if not isinstance(body.get('snapshot'),int) or isinstance(body.get('snapshot'),bool) or body['snapshot']<1 or not isinstance(body.get('pending'),list) or not isinstance(body.get('scenes'),list):raise ValueError('invalid bounded journal state')
        encoded=json.dumps(body,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
        if j.get('sha256')!=hashlib.sha256(encoded).hexdigest() or body.get('version')!=1 or body.get('session')!=self.session:
            raise ValueError('journal checksum/version/compositor session differs')
        return body
    def write(self,body):
        if body.get('version')!=1 or body.get('session')!=self.session:raise ValueError('explicit journal session required')
        encoded=json.dumps(body,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
        content=json.dumps({'body':body,'sha256':hashlib.sha256(encoded).hexdigest()},sort_keys=True,separators=(',',':'),allow_nan=False).encode()
        if len(content)>MAX_BYTES:raise ValueError('journal exceeds bound')
        atomic_write(self.path,content)

def atomic_write(path,data):
    path=Path(path);private_directory(path.parent)
    staging=path.parent/('.'+path.name+'-'+uuid.uuid4().hex+'.tmp')
    fd=None
    try:
        fd=os.open(staging,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
        with os.fdopen(fd,'wb') as out:fd=None;out.write(data);out.flush();os.fsync(out.fileno())
        if path.is_symlink():raise ValueError('runtime destination symlink refused')
        staging.replace(path)
        directory=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
        try:os.fsync(directory)
        finally:os.close(directory)
    finally:
        if fd is not None:os.close(fd)
        staging.unlink(missing_ok=True)

def unresolved(body):return bool(body and (body.get('pending') or body.get('scenes')))

class RuntimeLease:
    def __init__(self,root,session):
        self.root=private_directory(root,create=True);self.session=session;self.fd=None
        self.nonce=uuid.uuid4().hex;self.owner_path=self.root/'owner.json';self.socket=self.root/'api.sock'
        if len(os.fsencode(self.socket))>=108:raise ValueError('runtime socket path exceeds bound')
        try:
            self.fd=os.open(self.root/'runtime.lock',os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
            s=os.fstat(self.fd)
            if not stat.S_ISREG(s.st_mode) or s.st_uid!=os.getuid() or s.st_mode&0o077:raise ValueError('unsafe runtime lease inode')
            fcntl.flock(self.fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            try:old=read_private(self.owner_path)
            except FileNotFoundError:old=None
            if old and (old.get('session')!=session or process_start(old.get('pid',0))==old.get('start')):
                raise ValueError('different compositor session or exact live owner')
            if self.socket.exists() or self.socket.is_symlink():
                s=self.socket.lstat()
                if (not old or not stat.S_ISSOCK(s.st_mode) or s.st_uid!=os.getuid()
                    or old.get('socket')!=[s.st_dev,s.st_ino]):raise ValueError('unowned/replaced runtime socket')
                # A passed/inherited listener can outlive its archived owner.
                # Exact inode alone is not proof that no actor still serves it.
                probe=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
                try:
                    probe.settimeout(.1)
                    try:probe.connect(str(self.socket))
                    except ConnectionRefusedError:pass
                    else:raise ValueError('stale owner still has a live socket listener')
                finally:probe.close()
                current=self.socket.lstat()
                if [current.st_dev,current.st_ino]!=old['socket']:raise ValueError('stale socket changed during listener probe')
                self.socket.unlink()
            self.owner={'pid':os.getpid(),'start':process_start(os.getpid()),'nonce':self.nonce,'session':session,'socket':None}
            self.publish_owner()
        except Exception:
            if self.fd is not None:os.close(self.fd);self.fd=None
            raise
    def publish_owner(self):atomic_write(self.owner_path,json.dumps(self.owner,allow_nan=False).encode())
    def bound(self,identity):self.owner['socket']=list(identity);self.publish_owner()
    def close(self):
        if self.fd is None:return
        try:
            try:
                current=read_private(self.owner_path)
                if current.get('nonce')==self.nonce:self.owner_path.unlink()
            except FileNotFoundError:pass
        finally:os.close(self.fd);self.fd=None

class RuntimeService:
    def __init__(self,root,session,factory,context_provider,*,recovery=None):
        if not isinstance(session,str) or not session:raise ValueError('explicit compositor session required')
        self.lease=RuntimeLease(root,session);self.store=JournalStore(self.lease.root,session)
        self.session=session;self.stop_requested=threading.Event();self.failure=None;self.closed=False;self.snapshot_serial=0
        self.manager=self.frontend=None
        try:
            previous=self.store.read()
            if previous:self.snapshot_serial=previous['snapshot']
            if unresolved(previous):
                if recovery is None:raise RuntimeError('unresolved durable requests require explicit fresh-native recovery')
                recovery(previous) # explicit caller; no journal-native authority implied
            self.manager=SceneManager(factory,persist=self.persist,journal=lambda _:self.persist())
            self.persist()
            self.frontend=SocketFrontend(self.lease.socket,self.manager,context_provider,on_stop=self.stop_requested.set)
            self.lease.bound(self.frontend.socket_identity)
        except Exception:
            if self.frontend:self.frontend.close()
            self.lease.close()
            raise
    def snapshot(self):
        m=self.manager
        scenes=[]
        for a in m.actors:
            r=a.controller.current
            if r:scenes.append({'actor':a.number,'token':r.token,'operation':r.operation,'requested':list(r.requested),
                'members':[list(key(w)) for w in r.members],'sources':r.sources,'context':r.context,
                'validated':r.validated,'acceptedOperation':r.accepted_operation,'profile':r.profile,'results':r.results})
        return {'version':1,'session':self.session,'snapshot':self.snapshot_serial,'serial':m.serial,
            'receipts':[[list(k),r] for k,r in sorted(m.receipts.items())],
            'pending':[{'receipt':p['receipt'],'operation':p['command'],'captured':list(p['captured']),
                'scope':[list(k) for k in sorted(p['scope'])],'direction':asdict(p['direction']),'single':p['single']} for p in m.pending.values()],
            'scenes':scenes,'ingressHistory':m.ingress_history,'failure':self.failure}
    def persist(self):
        with self.manager.lock:
            if self.manager.persistence_failed:raise RuntimeError('durable journal previously failed; native authority revoked')
            self.snapshot_serial+=1
            try:self.store.write(self.snapshot())
            except Exception as error:
                self.failure='durable journal: '+str(error);self.manager.persistence_failed=True;self.manager.closed=True
                self.stop_requested.set()
                raise RuntimeError(self.failure) from error
    def start(self):self.frontend.start()
    def run(self):
        self.start()
        try:
            while not self.stop_requested.wait(.1):self.manager.watchdog()
        finally:self.close()
    def close(self):
        if self.closed:
            if self.failure:raise RuntimeError(self.failure)
            return
        self.closed=True;errors=[]
        try:self.manager.close()
        except Exception as error:errors.append(str(error))
        try:self.frontend.close(close_manager=False)
        except Exception as error:errors.append(str(error))
        try:self.lease.close()
        except Exception as error:errors.append(str(error))
        if errors or self.failure:
            self.failure='; '.join(([self.failure] if self.failure else [])+errors)
            raise RuntimeError(self.failure)

def stop_runtime(root,session,*,timeout=1):
    """No startup/creation/fallback. Silent absence only after own idle proof."""
    root=Path(root)
    if not root.exists():return {'ok':True,'alreadyStopped':True}
    private_directory(root);api=root/'api.sock'
    try:owner=read_private(root/'owner.json')
    except FileNotFoundError:owner=None
    if api.exists() or api.is_symlink():
        s=api.lstat()
        if (not owner or not stat.S_ISSOCK(s.st_mode) or s.st_uid!=os.getuid() or s.st_mode&0o077
                or owner.get('session')!=session or owner.get('socket')!=[s.st_dev,s.st_ino]
                or process_start(owner.get('pid',0))!=owner.get('start')):
            raise ValueError('unknown/replaced socket or exact runtime owner')
        with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as connection:
            connection.settimeout(timeout);connection.connect(str(api))
            import struct
            pid,uid,_=struct.unpack('3i',connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
            now=api.lstat()
            if pid!=owner['pid'] or uid!=os.getuid() or [now.st_dev,now.st_ino]!=owner['socket']:
                raise ValueError('connected stop peer differs from exact runtime owner')
            connection.sendall(b'{"command":"stop"}\n')
            data=bytearray()
            while b'\n' not in data:
                part=connection.recv(8193-len(data))
                if not part or len(data)+len(part)>8192:raise ValueError('incomplete/unbounded stop response')
                data.extend(part)
            result=json.loads(bytes(data).split(b'\n',1)[0])
            if not result.get('ok'):raise RuntimeError('service refused stop: '+str(result))
            return result
    if owner and (owner.get('session')!=session or process_start(owner.get('pid',0))==owner.get('start')):
        raise RuntimeError('service owner live or compositor session differs but socket absent')
    if unresolved(JournalStore(root,session).read()):raise RuntimeError('unresolved durable requests; idle stop cannot discard them')
    lock=root/'runtime.lock'
    if lock.exists():
        fd=os.open(lock,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
        try:
            s=os.fstat(fd)
            if s.st_uid!=os.getuid() or not stat.S_ISREG(s.st_mode) or s.st_mode&0o077:raise ValueError('unsafe idle lease')
            fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        finally:os.close(fd)
    return {'ok':True,'alreadyStopped':True}
