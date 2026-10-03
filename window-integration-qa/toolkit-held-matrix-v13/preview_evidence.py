"""Durable read-only observations; never moves input or grants feature authority."""
import json
import os
from pathlib import Path
import stat
import time

class PreviewEvidence:
    def __init__(self,route,shell_identity,target):
        self.route=route;self.index=0;self.closed=False
        folder=Path(route.folder);info=folder.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid!=os.getuid() or info.st_mode&0o077 or folder.resolve()!=folder.absolute():
            raise RuntimeError('Exact owned private preview evidence directory required')
        self.path=folder/'preview-motion-observation.jsonl'
        self.fd=os.open(self.path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
        try:self.emit('begin',dict(shellIdentity=shell_identity,target=target,inputIdentity=route.pointer.identity,extents=route.extents,pointerKnownDown=sorted(route.pointer.down),keyboardKnownDown=sorted(route.keyboard.down),geometryDoesNotAuthorizeClick=True))
        except BaseException:os.close(self.fd);self.closed=True;raise
    def emit(self,event,body):
        if self.closed or self.index>=512:raise RuntimeError('Bounded complete preview evidence required')
        row=dict(index=self.index,event=event,timeNs=time.monotonic_ns(),**body)
        data=(json.dumps(row,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
        if len(data)>4*1024*1024:raise RuntimeError('Bounded preview evidence record required')
        offset=0
        while offset<len(data):
            written=os.write(self.fd,data[offset:])
            if written<=0:raise OSError('Complete preview evidence write required')
            offset+=written
        os.fsync(self.fd)
        self.route.record('retained preview '+event,dict(observationPath=str(self.path),observationIndex=self.index,timeNs=row['timeNs'],nativeFeatureOutcomeNotInferred=True))
        self.index+=1
        return row
    def __enter__(self):return self
    def __exit__(self,kind,error,traceback):
        try:self.emit('terminal',dict(result='error' if error is not None else 'completed',error=repr(error) if error is not None else None,featureAcceptedNotInferred=True))
        finally:os.close(self.fd);self.closed=True
        return False
