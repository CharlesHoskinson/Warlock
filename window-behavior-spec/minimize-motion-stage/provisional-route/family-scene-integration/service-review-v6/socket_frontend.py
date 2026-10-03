"""Private staged UNIX API. Explicit manager/context provider; no autostart."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import socket
import stat
import struct
import threading

class SocketFrontend:
    def __init__(self,path,manager,context_provider,*,max_pending=32):
        self.path=Path(path)
        parent=self.path.parent.stat()
        if not stat.S_ISDIR(parent.st_mode) or parent.st_uid!=os.getuid() or parent.st_mode&0o077:
            raise ValueError('API parent must be a private directory owned by this UID')
        if len(os.fsencode(self.path))>=108:raise ValueError('UNIX socket path exceeds bound')
        if self.path.exists() or self.path.is_symlink():raise FileExistsError(self.path)
        self.manager=manager;self.context_provider=context_provider
        self.max_pending=max_pending
        self.lock=threading.Lock();self.context_jobs=0
        self.workers=ThreadPoolExecutor(max_workers=4,thread_name_prefix='motion-context')
        self.listener=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        self.listener.bind(str(self.path));self.path.chmod(0o600)
        self.socket_identity=(self.path.stat().st_dev,self.path.stat().st_ino)
        self.listener.listen(16);self.listener.settimeout(.1)
        self.closed=False;self.accept_thread=None;self.connections=set();self.client_threads=set()
    def start(self):
        if self.accept_thread:raise RuntimeError('API already started')
        self.accept_thread=threading.Thread(target=self.accept,daemon=True);self.accept_thread.start()
    def accept(self):
        while not self.closed:
            try:connection,_=self.listener.accept()
            except socket.timeout:continue
            except OSError:return
            _,uid,_=struct.unpack('3i',connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
            with self.lock:
                if uid!=os.getuid() or len(self.connections)>=16:connection.close();continue
                self.connections.add(connection)
                thread=threading.Thread(target=self.client,args=(connection,),daemon=True)
                self.client_threads.add(thread)
            thread.start()
    def client(self,connection):
        try:
            connection.settimeout(1)
            data=bytearray()
            while b'\n' not in data:
                chunk=connection.recv(8193-len(data))
                if not chunk:raise ValueError('incomplete API request')
                data.extend(chunk)
                if len(data)>8192:raise ValueError('API request exceeds bound')
            line,extra=bytes(data).split(b'\n',1)
            if extra:raise ValueError('one API request per connection')
            request=json.loads(line)
            if not isinstance(request,dict):raise ValueError('API request must be object')
            result=self.dispatch(request)
            connection.sendall(json.dumps(result,allow_nan=False,separators=(',',':')).encode()+b'\n')
        except Exception as error:
            try:connection.sendall(json.dumps({'ok':False,'accepted':False,'error':str(error)}).encode()+b'\n')
            except OSError:pass
        finally:
            connection.close()
            with self.lock:self.connections.discard(connection);self.client_threads.discard(threading.current_thread())
    def dispatch(self,request):
        command=request.get('command')
        if command=='request':
            allowed={'command','operation','address','stableId','pid','single'}
            if set(request)-allowed:raise ValueError('unsupported frontend field; context is service-owned')
            if not isinstance(request.get('single',False),bool):raise ValueError('single must be boolean')
            with self.lock:
                if self.closed or self.context_jobs>=self.max_pending:raise RuntimeError('context queue unavailable')
                self.context_jobs+=1
            try:
                result=self.manager.reserve(request.get('operation'),request.get('address'),request.get('stableId'),request.get('pid'),single=request.get('single',False))
                self.workers.submit(self.context,result['receipt'],dict(request))
                return result
            except Exception:
                with self.lock:self.context_jobs-=1
                raise
        if command=='state' and set(request)=={'command'}:
            with self.manager.lock:
                return {'ok':True,'actors':self.manager.state(),
                    'pendingReceipts':list(self.manager.pending),'ingressHistory':list(self.manager.ingress_history)}
        raise ValueError('unsupported frontend command')
    def context(self,receipt,request):
        try:
            context=self.context_provider(request)
            if context is None:raise ValueError('native context observation missing')
            self.manager.activate(receipt,context=context)
        except Exception as error:self.manager.fail_ingress(receipt,str(error))
        finally:
            with self.lock:self.context_jobs-=1
    def close(self):
        with self.lock:
            self.closed=True
            connections=list(self.connections)
        self.listener.close()
        for connection in connections:
            try:connection.shutdown(socket.SHUT_RDWR)
            except OSError:pass
        if self.accept_thread:self.accept_thread.join(timeout=1)
        self.workers.shutdown(wait=True,cancel_futures=False)
        error=None
        try:self.manager.close()
        except Exception as failure:error=failure
        try:
            current=self.path.lstat()
            if (current.st_dev,current.st_ino)==self.socket_identity and stat.S_ISSOCK(current.st_mode):self.path.unlink()
        except FileNotFoundError:pass
        if error:raise error
