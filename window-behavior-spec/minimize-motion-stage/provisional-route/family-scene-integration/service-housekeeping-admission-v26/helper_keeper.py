"""Headless descriptor keeper. No process/socket/files created on import."""
import array
import json
import os
from pathlib import Path
import signal
import socket
import struct
import time
import re

GROUP=4
MAX_PACKET=32768


def send(connection,body,fd=None):
    data=json.dumps(body,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
    if len(data)>MAX_PACKET:raise ValueError('bounded keeper packet required')
    ancillary=[] if fd is None else [(socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array('i',[fd]))]
    if connection.sendmsg([data],ancillary)!=len(data):raise RuntimeError('partial keeper packet')


def receive(connection,expected_pid,expected_uid):
    data,ancillary,flags,_=connection.recvmsg(MAX_PACKET+1,socket.CMSG_SPACE(12)+socket.CMSG_SPACE(4))
    descriptors=[];credential=None
    try:
        for level,kind,value in ancillary:
            if level!=socket.SOL_SOCKET:raise ValueError('unexpected keeper ancillary level')
            if kind==socket.SCM_RIGHTS:
                items=array.array('i');items.frombytes(value[:len(value)//items.itemsize*items.itemsize]);descriptors.extend(items)
            elif kind==socket.SCM_CREDENTIALS:
                if credential is not None:raise ValueError('duplicate keeper credentials')
                credential=struct.unpack('3i',value)
            else:raise ValueError('unexpected keeper ancillary data')
        if not data:
            if descriptors:raise ValueError('descriptor on keeper EOF')
            return None,None
        if flags&(socket.MSG_TRUNC|socket.MSG_CTRUNC) or len(data)>MAX_PACKET or len(descriptors)>1:raise ValueError('truncated/unbounded keeper message')
        if credential is None or credential[0]!=expected_pid or credential[1]!=expected_uid:raise ValueError('keeper sender is not exact kernel peer PID/UID')
        value=json.loads(data)
        if not isinstance(value,dict):raise ValueError('keeper object packet required')
        fd=descriptors.pop() if descriptors else None
        if fd is not None:os.set_inheritable(fd,False)
        return value,fd
    finally:
        for fd in descriptors:os.close(fd)


def group_empty(pidfd):
    try:signal.pidfd_send_signal(pidfd,0,None,GROUP);return False
    except ProcessLookupError:return True


def close_group(pidfd,timeout=2):
    if group_empty(pidfd):return {'groupEmpty':True,'signaled':False,'forced':False}
    try:signal.pidfd_send_signal(pidfd,signal.SIGTERM,None,GROUP)
    except ProcessLookupError:return {'groupEmpty':True,'signaled':False,'forced':False}
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        if group_empty(pidfd):return {'groupEmpty':True,'signaled':True,'forced':False}
        time.sleep(.005)
    try:signal.pidfd_send_signal(pidfd,signal.SIGKILL,None,GROUP)
    except ProcessLookupError:return {'groupEmpty':True,'signaled':True,'forced':False}
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        if group_empty(pidfd):return {'groupEmpty':True,'signaled':True,'forced':True}
        time.sleep(.005)
    raise RuntimeError('exact retained group not empty; closure refused')


def pidfd_pid(fd):
    value=Path(f'/proc/self/fdinfo/{fd}').read_text()
    fields=dict(line.split(':',1) for line in value.splitlines() if ':' in line)
    pid=int(fields.get('Pid','-1'))
    if pid<=0:raise ValueError('live exact leader pidfd required on registration')
    return pid


def private_terminal(root,root_identity,name,body):
    directory=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
    temporary=name+'.tmp';fd=None
    try:
        info=os.fstat(directory)
        if [info.st_dev,info.st_ino]!=root_identity or info.st_uid!=os.getuid() or info.st_mode&0o077:raise ValueError('keeper root identity/private mode changed')
        data=json.dumps(body,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
        if len(data)>1048576:raise ValueError('keeper terminal exceeds bound')
        fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=directory)
        with os.fdopen(fd,'wb') as output:fd=None;output.write(data);output.flush();os.fsync(output.fileno())
        os.rename(temporary,name,src_dir_fd=directory,dst_dir_fd=directory);os.fsync(directory)
    finally:
        if fd is not None:os.close(fd)
        os.close(directory)


def serve(connection,*,service_pid,service_start,nonce,root,root_identity,keeper_start):
    if type(service_pid) is not int or service_pid<1 or type(service_start) is not int or service_start<1 or type(keeper_start) is not int or keeper_start<1:raise ValueError('typed keeper/service lifetimes required')
    if not isinstance(nonce,str) or not re.fullmatch('[0-9a-f]{32}',nonce):raise ValueError('exact bounded keeper nonce required')
    connection.setsockopt(socket.SOL_SOCKET,socket.SO_PASSCRED,1)
    groups={};history=[];registrations=0;normal=False
    send(connection,{'event':'keeperReady','pid':os.getpid(),'start':keeper_start,'nonce':nonce})
    try:
        while True:
            request,fd=receive(connection,service_pid,os.getuid())
            if request is None:break
            try:
                command=request.get('command')
                if command in ('register','complete') and (not isinstance(request.get('job'),str) or not re.fullmatch('[0-9a-f]{32}',request['job'])):raise ValueError('typed unique job nonce required')
                fields=Path(f'/proc/{service_pid}/stat').read_text().rsplit(') ',1)[1].split()
                if int(fields[19])!=service_start:raise ValueError('selected service lifetime changed')
                if command=='register':
                    if set(request)!={'command','job','pid','start'} or fd is None or len(groups)>=256 or request['job'] in groups:raise ValueError('complete bounded unique keeper registration required')
                    pid=pidfd_pid(fd)
                    if type(request['pid']) is not int or pid!=request['pid'] or type(request['start']) is not int or request['start']<1:raise ValueError('typed exact leader identity required')
                    fields=Path(f'/proc/{pid}/stat').read_text().rsplit(') ',1)[1].split()
                    if int(fields[19])!=request['start'] or int(fields[2])!=pid or int(fields[3])!=pid:raise ValueError('leader must own exact private process group/session')
                    status=dict(line.split(':',1) for line in Path(f'/proc/{pid}/status').read_text().splitlines() if ':' in line)
                    if status.get('NoNewPrivs','').strip()!='1' or status.get('Seccomp','').strip()!='2' or int(status['Uid'].split()[0])!=os.getuid():raise ValueError('confined same-UID gated leader required')
                    if group_empty(fd):raise ValueError('leader group exited before registration')
                    groups[request['job']]={'fd':fd,'pid':pid,'start':request['start']};fd=None;registrations+=1
                    send(connection,{'ok':True,'job':request['job']})
                elif command=='complete':
                    if set(request)!={'command','job'} or fd is not None or request['job'] not in groups:raise ValueError('exact existing completed job required')
                    row=groups[request['job']]
                    if not group_empty(row['fd']):raise ValueError('job still has group descendants; normal completion refused')
                    groups.pop(request['job']);os.close(row.pop('fd'));history.append({'job':request['job'],**row,'groupEmpty':True,'normalCompletion':True});history=history[-256:]
                    send(connection,{'ok':True,'job':request['job']})
                elif command=='stop':
                    if set(request)!={'command'} or fd is not None or groups:raise ValueError('normal keeper stop requires no outstanding helper groups')
                    normal=True;send(connection,{'ok':True,'stopping':True});break
                else:raise ValueError('unknown keeper command')
            finally:
                if fd is not None:os.close(fd)
    finally:
        # No success record can be published if one exact group fails closure.
        for job,row in groups.items():
            result=close_group(row['fd']);history.append({'job':job,'pid':row['pid'],'start':row['start'],**result,'normalCompletion':False})
        terminal={'keeperPID':os.getpid(),'keeperStart':keeper_start,'nonce':nonce,'rootIdentity':root_identity,
            'servicePID':service_pid,'serviceStart':service_start,'allGroupsEmpty':True,'normalStop':normal,
            'registrations':registrations,'jobs':history[-512:],'closedNs':time.monotonic_ns()}
        private_terminal(root,root_identity,'keeper-'+nonce+'.json',terminal)
        for row in groups.values():os.close(row['fd'])
        connection.close()
