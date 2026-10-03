"""Observe only an authenticated wrapper's own child; never redirect product FDs."""
import ctypes
import errno
import hashlib
import json
import os
from pathlib import Path
import platform
import select
import signal
import stat
import time

MAX_WRITE=1048576
MAX_LOG=33554432
MAX_RECORDS=2048
TRACEME=0;SYSCALL=24;DETACH=17;SETOPTIONS=0x4200;GET_SYSCALL_INFO=0x420e
TRACESYSGOOD=1;TRACEEXEC=0x10;EVENT_EXEC=4
ARCH_X86_64=0xc000003e

class IOVec(ctypes.Structure):
    _fields_=[('base',ctypes.c_void_p),('length',ctypes.c_size_t)]
class Entry(ctypes.Structure):
    _fields_=[('nr',ctypes.c_uint64),('args',ctypes.c_uint64*6)]
class Exit(ctypes.Structure):
    _fields_=[('rval',ctypes.c_int64),('is_error',ctypes.c_uint8)]
class Seccomp(ctypes.Structure):
    _fields_=[('nr',ctypes.c_uint64),('args',ctypes.c_uint64*6),('ret_data',ctypes.c_uint32)]
class Data(ctypes.Union):
    _fields_=[('entry',Entry),('exit',Exit),('seccomp',Seccomp)]
class Info(ctypes.Structure):
    _fields_=[('op',ctypes.c_uint8),('pad',ctypes.c_uint8*3),('arch',ctypes.c_uint32),('ip',ctypes.c_uint64),('sp',ctypes.c_uint64),('data',Data)]

def libc():
    c=ctypes.CDLL('libc.so.6',use_errno=True)
    c.ptrace.restype=ctypes.c_long;c.ptrace.argtypes=[ctypes.c_uint,ctypes.c_int,ctypes.c_void_p,ctypes.c_void_p]
    c.process_vm_readv.restype=ctypes.c_ssize_t;c.process_vm_readv.argtypes=[ctypes.c_int,ctypes.POINTER(IOVec),ctypes.c_ulong,ctypes.POINTER(IOVec),ctypes.c_ulong,ctypes.c_ulong]
    return c

def ptrace(c,request,pid,addr=0,data=0):
    ctypes.set_errno(0)
    out=c.ptrace(request,pid,ctypes.c_void_p(addr),ctypes.c_void_p(data))
    if out<0:raise OSError(ctypes.get_errno(),os.strerror(ctypes.get_errno()))
    return out

def child_bootstrap():
    """Caller already verified source/gate; only direct parent may trace this PID."""
    if platform.machine()!='x86_64':raise RuntimeError('Exact reviewed syscall architecture required')
    ptrace(libc(),TRACEME,0);os.kill(os.getpid(),signal.SIGSTOP)

def proc(identity):
    try:
        raw=Path('/proc',str(identity['pid']),'stat').read_text();head,tail=raw.rsplit(') ',1);fields=tail.split()
    except (FileNotFoundError,ProcessLookupError):return dict(kind='absent',rawStat=None,exitCodeKnown=False)
    if head.split(' ',1)[0]!=str(identity['pid']) or len(fields)<20:raise RuntimeError('Complete exact observed process stat required')
    if str(fields[19])!=str(identity['start']):return dict(kind='reused',rawStat=raw,exitCodeKnown=False)
    if fields[0] not in ('R','S','D','T','t','Z','X','x','K','W','P','I'):raise RuntimeError('Unknown process state')
    out=dict(kind='exact',state=fields[0],rawStat=raw,exitCodeKnown=False)
    if fields[0]=='Z' and len(fields)>=50:out.update(exitCodeKnown=True,kernelWaitStatus=int(fields[49]))
    return out

def fd_witness(pid,fd):
    path=Path('/proc',str(pid),'fd',str(fd));info=path.stat()
    return dict(device=info.st_dev,inode=info.st_ino,mode=info.st_mode,uid=info.st_uid,link=os.readlink(path))

def stamp():return dict(monotonicNs=time.monotonic_ns(),utcNs=time.time_ns())

def witness(info):return (info.st_dev,info.st_ino,info.st_uid,info.st_mode,info.st_size,info.st_mtime_ns,info.st_ctime_ns)

class Journal:
    def __init__(self,path):
        self.path=Path(path);parent=self.path.parent.lstat()
        if not stat.S_ISDIR(parent.st_mode) or parent.st_uid!=os.getuid() or stat.S_IMODE(parent.st_mode)!=0o700:raise RuntimeError('Exact owned private diagnostic directory required')
        self.fd=os.open(self.path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600);self.identity=os.fstat(self.fd);self.size=0;self.count=0
    def emit(self,event,body):
        if self.count>=MAX_RECORDS:raise RuntimeError('Bounded diagnostic record count exceeded')
        raw=(json.dumps(dict(index=self.count,event=event,**stamp(),**body),separators=(',',':'),allow_nan=False)+'\n').encode()
        if len(raw)>4194304 or self.size+len(raw)>MAX_LOG:raise RuntimeError('Bounded complete diagnostic bytes exceeded')
        now=os.fstat(self.fd);path=self.path.lstat()
        if (now.st_dev,now.st_ino)!=(self.identity.st_dev,self.identity.st_ino) or now.st_uid!=os.getuid() or stat.S_IMODE(now.st_mode)!=0o600 or now.st_size!=self.size or witness(now)!=witness(path):raise RuntimeError('Exact diagnostic file witness changed')
        offset=0
        while offset<len(raw):
            written=os.write(self.fd,raw[offset:])
            if written<=0:raise RuntimeError('Complete diagnostic write required')
            offset+=written
        os.fsync(self.fd);self.size+=len(raw);self.count+=1
        return self.count-1
    def close(self):
        if self.fd is not None:os.close(self.fd);self.fd=None

class Observer:
    def __init__(self,journal,delegate,parent,qs,allowed_exec,metadata):
        if platform.machine()!='x86_64' or ctypes.sizeof(Info)!=88:raise RuntimeError('Exact Linux x86_64 syscall witness required')
        for identity in (delegate,parent,qs):
            if type(identity.get('pid')) is not int or identity['pid']<=0 or not str(identity.get('start','')).isdigit():raise RuntimeError('Exact selected observer identities required')
        raw=proc(delegate)
        if raw['kind']!='exact' or int(raw['rawStat'].rsplit(') ',1)[1].split()[1])!=os.getpid():raise RuntimeError('Only own exact gated delegate may be observed')
        self.journal=journal;self.delegate=delegate;self.parent=parent;self.qs=qs;self.allowed_exec=allowed_exec;self.exec_index=0;self.errors=[];self.pending=None;self.captured=0;self.c=libc();self.stopped=False;self.terminal=False;self.parent_fd=None;self.detach_signal=0;self.initial_return=True;self.terminal_state=None
        self.fds={fd:fd_witness(delegate['pid'],fd) for fd in (1,2)}
        for fd in (1,2):
            if self.fds[fd]!=fd_witness(os.getpid(),fd):raise RuntimeError('Unchanged inherited stdio routing required')
        before=proc(parent)
        if before['kind']=='exact':
            self.parent_fd=os.pidfd_open(parent['pid'])
            if proc(parent)['kind']!='exact':os.close(self.parent_fd);self.parent_fd=None
        self.journal.emit('observer-bound',dict(delegate=delegate,parent=parent,qs=qs,metadata=metadata,stdio=self.fds,parentObservation=self.parent_state(),qsObservation=proc(qs),sourceRoutingChanged=False,schedulingPerturbed=True))
    def parent_state(self):
        value=proc(self.parent);value['pidfdObserved']=self.parent_fd is not None;value['pidfdExitObserved']=False
        if self.parent_fd is not None:
            p=select.poll();p.register(self.parent_fd,select.POLLIN);rows=p.poll(0)
            if rows and (len(rows)!=1 or rows[0][0]!=self.parent_fd or not(rows[0][1]&select.POLLIN) or rows[0][1]&~(select.POLLIN|select.POLLHUP)):raise RuntimeError('Unknown exact parent pidfd event')
            value['pidfdExitObserved']=bool(rows)
        return value
    def state(self):return dict(parentObservation=self.parent_state(),qsObservation=proc(self.qs))
    def memory(self,address,size):
        if not 0<=size<=MAX_WRITE:raise RuntimeError('Complete bounded original write memory required')
        if size==0:return b''
        target=ctypes.create_string_buffer(size);local=IOVec(ctypes.cast(target,ctypes.c_void_p),size);remote=IOVec(address,size)
        count=self.c.process_vm_readv(self.delegate['pid'],ctypes.byref(local),1,ctypes.byref(remote),1,0)
        if count!=size:raise RuntimeError('Complete exact stopped-target memory read required')
        return target.raw[:size]
    def payload(self,nr,args):
        if nr==1:return [self.memory(args[1],args[2])]
        if args[2]>1024:raise RuntimeError('Bounded complete original writev vectors required')
        raw=self.memory(args[1],args[2]*ctypes.sizeof(IOVec));vectors=(IOVec*args[2]).from_buffer_copy(raw)
        if sum(v.length for v in vectors)>MAX_WRITE:raise RuntimeError('Bounded complete original writev bytes required')
        return [self.memory(v.base,v.length) for v in vectors]
    def syscall(self):
        info=Info();length=ptrace(self.c,GET_SYSCALL_INFO,self.delegate['pid'],ctypes.sizeof(info),ctypes.addressof(info))
        if info.arch!=ARCH_X86_64 or info.op not in (1,2) or length<(80 if info.op==1 else 33):raise RuntimeError('Exact supported kernel syscall information required')
        if info.op==1:
            if self.pending is not None:raise RuntimeError('Unexpected unpaired syscall entry')
            self.initial_return=False;nr=int(info.data.entry.nr);args=list(info.data.entry.args);self.pending=dict(nr=nr,write=None)
            if nr in (1,20) and args[0] in (1,2):
                fd=int(args[0]);fd_row=fd_witness(self.delegate['pid'],fd)
                if fd_row!=self.fds[fd]:raise RuntimeError('Original target stdio routing changed')
                vectors=self.payload(nr,args);raw=b''.join(vectors)
                self.pending['write']=dict(fd=fd,offered=len(raw),entry=self.journal.emit('stdio-write-entry',dict(nr=nr,fd=fd,args=args,vectorLengths=[len(v) for v in vectors],offeredBytesHex=raw.hex(),offeredSHA256=hashlib.sha256(raw).hexdigest(),fdWitness=fd_row,target=proc(self.delegate),execSeen=self.exec_index,**self.state())))
        else:
            if self.pending is None:
                if self.initial_return and self.exec_index==0 and info.data.exit.rval==0 and not info.data.exit.is_error:
                    self.initial_return=False;self.journal.emit('bootstrap-syscall-return',dict(kernelReturn=0,**self.state()));return
                raise RuntimeError('Unexpected unpaired syscall return')
            row=self.pending['write'];value=int(info.data.exit.rval);is_error=bool(info.data.exit.is_error)
            if row is not None:
                if is_error!=(value<0) or value>row['offered']:raise RuntimeError('Exact original write return/errno required')
                self.journal.emit('stdio-write-return',dict(entry=row['entry'],nr=self.pending['nr'],fd=row['fd'],kernelReturn=value,kernelIsError=is_error,errno=-value if is_error else None,deliveredCount=value if value>=0 else 0,offeredCount=row['offered'],**self.state()));self.captured+=1
            self.pending=None
    def exec(self):
        if self.exec_index>=len(self.allowed_exec):raise RuntimeError('Unexpected additional backend exec')
        expected=self.allowed_exec[self.exec_index];pid=self.delegate['pid'];actual_exe=str(Path('/proc',str(pid),'exe').resolve());raw=Path('/proc',str(pid),'cmdline').read_bytes();argv=[os.fsdecode(x) for x in raw.rstrip(b'\0').split(b'\0')]
        if proc(self.delegate)['kind']!='exact' or actual_exe!=expected['executable'] or hashlib.sha256(Path(actual_exe).read_bytes()).hexdigest()!=expected['executableSHA256'] or argv!=expected['argv']:raise RuntimeError('Exact unchanged backend exec/source/argv required')
        for fd in (1,2):
            if fd_witness(pid,fd)!=self.fds[fd]:raise RuntimeError('Exec changed original inherited stdio routing')
        self.journal.emit('backend-exec',dict(execOrdinal=self.exec_index,executable=actual_exe,argv=argv,identity=self.delegate,stdio=self.fds,**self.state()));self.exec_index+=1
    def run(self):
        status=None
        try:
            pid,status=os.waitpid(self.delegate['pid'],0)
            if os.WIFEXITED(status) or os.WIFSIGNALED(status):self.terminal=True
            if pid!=self.delegate['pid'] or not os.WIFSTOPPED(status) or os.WSTOPSIG(status)!=signal.SIGSTOP or proc(self.delegate)['kind']!='exact':raise RuntimeError('Exact own delegate bootstrap stop required')
            self.stopped=True;ptrace(self.c,SETOPTIONS,pid,0,TRACESYSGOOD|TRACEEXEC);self.journal.emit('bootstrap-stop',dict(status=status,identity=self.delegate,**self.state()));ptrace(self.c,SYSCALL,pid);self.stopped=False
            while True:
                pid,status=os.waitpid(self.delegate['pid'],0)
                if pid!=self.delegate['pid']:raise RuntimeError('Exact original delegate wait required')
                if os.WIFEXITED(status) or os.WIFSIGNALED(status):self.terminal=True;break
                if not os.WIFSTOPPED(status):raise RuntimeError('Unknown original delegate wait state')
                self.stopped=True;sig=os.WSTOPSIG(status);event=status>>16;self.detach_signal=sig if event==0 and sig!=(signal.SIGTRAP|0x80) else 0
                if sig==(signal.SIGTRAP|0x80) and event==0:self.syscall();forward=0
                elif sig==signal.SIGTRAP and event==EVENT_EXEC:self.exec();forward=0
                elif event==0 and sig not in (signal.SIGSTOP,signal.SIGTRAP):
                    self.journal.emit('genuine-signal-forward',dict(signal=sig,status=status,identity=self.delegate,**self.state()));forward=sig
                else:raise RuntimeError('Unknown ptrace stop; no diagnostic acceptance')
                ptrace(self.c,SYSCALL,pid,0,forward);self.stopped=False
        except BaseException as error:
            self.errors.append(repr(error))
            try:self.journal.emit('observer-error',dict(error=repr(error),status=status,identity=self.delegate,**self.state()))
            except BaseException as log_error:self.errors.append(repr(log_error))
            if not self.terminal:
                if self.stopped:
                    forward=self.detach_signal
                    try:ptrace(self.c,DETACH,self.delegate['pid'],0,forward)
                    except OSError as detach_error:self.errors.append(repr(detach_error))
                pid,status=os.waitpid(self.delegate['pid'],0)
                if pid!=self.delegate['pid'] or not(os.WIFEXITED(status) or os.WIFSIGNALED(status)):raise RuntimeError('Original delegate normal wait unavailable after observer refusal')
                self.terminal=True
        finally:
            try:self.terminal_state=self.state()
            except BaseException as error:self.errors.append(repr(error));self.terminal_state=dict(parentObservation=None,qsObservation=None)
            if self.parent_fd is not None:os.close(self.parent_fd);self.parent_fd=None
        if self.pending and self.pending['write'] is not None:self.errors.append('stdio syscall return missing at terminal')
        if self.exec_index!=len(self.allowed_exec):self.errors.append('unchanged backend exec chain incomplete')
        code=os.waitstatus_to_exitcode(status)
        complete=not self.errors
        self.journal.emit('delegate-wait-terminal',dict(identity=self.delegate,rawWaitStatus=status,exitCode=code,normalOriginalWait=True,complete=complete,errors=self.errors,stdioSyscalls=self.captured,execChain=self.exec_index,parentExitCodeUnavailable=not proc(self.parent)['exitCodeKnown'],**self.terminal_state))
        return status,dict(path=str(self.journal.path),complete=complete,errors=self.errors,stdioSyscalls=self.captured,exitCode=code,normalOriginalWait=True,schedulingPerturbed=True,productFdRoutingChanged=False)
