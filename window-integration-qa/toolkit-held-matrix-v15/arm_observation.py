"""Absolute-deadline IPC/full EOF and guarded atomic arm publication. Inert."""
import json,os,socket,stat,struct
from pathlib import Path
import helper_observer as observer
from arm_lock import remaining

def ipc_until(config,deadline):
    remaining(deadline)
    path=Path(config['socket']);info=path.lstat();identity=[info.st_dev,info.st_ino,info.st_uid]
    if not stat.S_ISSOCK(info.st_mode) or identity!=config['socketIdentity']:raise RuntimeError('Helper IPC socket replaced')
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)as connection:
        connection.settimeout(min(2,remaining(deadline)));connection.connect(str(path))
        pid,uid,gid=struct.unpack('3i',connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
        if pid!=config['compositor']['pid'] or uid!=os.getuid():raise RuntimeError('Helper IPC peer mismatch')
        connection.settimeout(min(2,remaining(deadline)));connection.sendall(b'j/version');reply=bytearray()
        while True:
            connection.settimeout(min(2,remaining(deadline)));chunk=connection.recv(4096)
            if not chunk:break
            reply.extend(chunk)
            if len(reply)>65536:raise RuntimeError('Helper IPC response too large')
    remaining(deadline);version=json.loads(reply)
    if not isinstance(version,dict) or not version or observer.digest_bytes(reply)!=config['versionSHA256']:raise RuntimeError('Helper actual compositor version changed')
    after=path.lstat()
    if [after.st_dev,after.st_ino,after.st_uid]!=identity:raise RuntimeError('Helper IPC socket replaced after full EOF')
    remaining(deadline)
    return {'request':'j/version','completeServerEOF':True,'peer':{'pid':pid,'uid':uid,'gid':gid},'socketIdentity':identity,'replySHA256':observer.digest_bytes(reply)}

def publish_until(path,value,deadline,evidence):
    remaining(deadline);temporary=path.with_name(path.name+'.new');created=False
    try:
        fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600);created=True
        with os.fdopen(fd,'w')as stream:
            json.dump(value,stream,indent=2);stream.write('\n');stream.flush()
        remaining(deadline)
        temporary.replace(path);created=False;evidence['atomicReplaceOccurred']=True
        # A delayed filesystem operation has no authority to dispatch a command.
        # Retain whether publication happened; never pretend it did not.
        remaining(deadline);evidence['publicationObservedBeforeDeadline']=True
    finally:
        if created:temporary.unlink()
