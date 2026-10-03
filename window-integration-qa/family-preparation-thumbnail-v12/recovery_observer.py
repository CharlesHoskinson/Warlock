"""Read-only recovery journals/resources retained AFTER each real durable write.

Wrapping persist/dispose never fabricates closure, modifies outcomes or calls a
native operation. Observer failures fail the collection and leave raw evidence.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import stat
import time

MAX_BYTES=268435456

def witness(info):
    return (info.st_dev,info.st_ino,info.st_uid,info.st_mode,info.st_size,info.st_mtime_ns,info.st_ctime_ns)

def retain_regular(path,destination,*,limit=MAX_BYTES,dir_fd=None):
    path=Path(path);selected=path if dir_fd is None else path.name
    fd=os.open(selected,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK,dir_fd=dir_fd)
    try:
        before=os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_uid!=os.getuid() or stat.S_IMODE(before.st_mode)!=0o600 or before.st_size>limit:
            raise ValueError('exact private bounded regular recovery material required')
        data=b''
        while len(data)<=limit:
            part=os.read(fd,min(1048576,limit+1-len(data)))
            if not part:break
            data+=part
        after=os.fstat(fd);named=os.stat(selected,dir_fd=dir_fd,follow_symlinks=False)
        if len(data)!=before.st_size or witness(before)!=witness(after) or witness(before)!=witness(named):
            raise ValueError('recovery material changed during exact EOF read')
    finally:os.close(fd)
    selected=Path(destination);selected.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    output=os.open(selected,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
    with os.fdopen(output,'wb') as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
    return dict(path=str(path),retained=str(selected),sha256=hashlib.sha256(data).hexdigest(),device=before.st_dev,inode=before.st_ino,uid=before.st_uid,mode=stat.S_IMODE(before.st_mode),bytes=len(data),completeEOF=True)

class RecoveryArchive:
    def __init__(self,coordinator,destination):
        self.coordinator=coordinator;self.destination=Path(destination);self.destination.mkdir(mode=0o700);self.serial=0
        info=self.destination.lstat()
        if self.destination.resolve()!=self.destination.absolute() or info.st_uid!=os.getuid() or stat.S_IMODE(info.st_mode)!=0o700:raise ValueError('owned fresh recovery evidence directory required')
    def snapshot(self,phase):
        self.serial+=1;folder=self.destination/f'{self.serial:04d}-{phase}';folder.mkdir(mode=0o700)
        # Persist raw bytes before any semantic comparison can fail.
        raw=retain_regular(self.coordinator.store.path,folder/'journal.json',limit=8388608)
        record={'phase':phase,'observedNs':time.monotonic_ns(),'journal':raw,'resources':[],'nativeAuthority':False}
        try:
            body=self.coordinator.store.read();record['body']=copy.deepcopy(body)
            if body!=self.coordinator.body:raise ValueError('observer journal does not equal durable coordinator body')
            root=Path(self.coordinator.factory.root)
            for row in body['actorResources']:
                owned=row['directory'];path=Path(owned['path']);entry={'actor':row['actor'],'directory':copy.deepcopy(owned),'phase':row['phase'],'files':[]};record['resources'].append(entry)
                if path.parent!=root/'actors':raise ValueError('resource archive escaped exact actor root')
                try:parent=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
                except FileNotFoundError:
                    if owned['parentIdentity'] is not None:raise
                    entry['exists']=False;continue
                child=None
                try:
                    p=os.fstat(parent)
                    if [p.st_dev,p.st_ino]!=owned['parentIdentity'] or p.st_uid!=os.getuid() or stat.S_IMODE(p.st_mode)!=0o700:raise ValueError('archive actor parent anchor changed')
                    try:child=os.open(path.name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent)
                    except FileNotFoundError:entry['exists']=False;continue
                    info=os.fstat(child);entry['exists']=True
                    if [info.st_dev,info.st_ino]!=owned['identity'] or info.st_uid!=os.getuid() or stat.S_IMODE(info.st_mode)!=0o700:raise ValueError('archive actor anchor changed')
                    names=sorted(os.listdir(child))
                    for name in names:
                        entry['files'].append(retain_regular(path/name,folder/'actors'/str(row['actor'])/name,dir_fd=child))
                    named=os.stat(path.name,dir_fd=parent,follow_symlinks=False)
                    if (info.st_dev,info.st_ino)!=(named.st_dev,named.st_ino) or sorted(os.listdir(child))!=names:raise ValueError('archive actor namespace changed')
                finally:
                    if child is not None:os.close(child)
                    os.close(parent)
            lease=getattr(self.coordinator.lease_verify,'__self__',None)
            expected=getattr(lease,'root_identity',None)
            descriptor=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
            try:
                anchored=os.fstat(descriptor)
                if expected!=(anchored.st_dev,anchored.st_ino):raise ValueError('recovery evidence requires current actual lease root anchor')
                for name in ('owner.json','runtime.lock'):
                    record[name]=retain_regular(root/name,folder/name,limit=1048576,dir_fd=descriptor)
                named=root.lstat()
                if (named.st_dev,named.st_ino)!=(anchored.st_dev,anchored.st_ino):raise ValueError('recovery evidence root anchor changed')
            finally:os.close(descriptor)
        except BaseException as error:
            record['error']=repr(error);self.write(folder/'observation.json',record);raise
        self.write(folder/'observation.json',record);return record
    @staticmethod
    def write(path,record):
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
        with os.fdopen(fd,'w') as stream:json.dump(record,stream,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    def attach(self):
        original_persist=self.coordinator.persist;original_dispose=self.coordinator.dispose
        def persist():
            result=original_persist();self.snapshot('persisted');return result
        def dispose(*args,**kwargs):
            if not kwargs.get('inspection_only'):self.snapshot('before-dispose')
            result=original_dispose(*args,**kwargs)
            if not kwargs.get('inspection_only'):self.snapshot('after-dispose')
            return result
        self.coordinator.persist=persist;self.coordinator.dispose=dispose
        return self.coordinator
