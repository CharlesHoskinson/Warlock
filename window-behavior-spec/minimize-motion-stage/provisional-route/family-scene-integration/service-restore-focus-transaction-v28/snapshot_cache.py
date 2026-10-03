"""Private persistent whole-atlas pairs. No compositor calls or import effects."""
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import struct
import uuid
from scene_controller import key,rectangle

class SnapshotCache:
    def __init__(self,root,validate_snapshot,*,session="diagnostic-test"):
        if not isinstance(session,str) or not session:raise ValueError("compositor cache session required")
        self.session=session
        self.root=Path(root)
        self.root.mkdir(mode=0o700,parents=True,exist_ok=True)
        info=self.root.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid!=os.getuid() or info.st_mode&0o077:raise ValueError('persistent cache must be a private owned directory')
        self.validate_snapshot=validate_snapshot
    def stem(self,window):
        address,sid,pid=key(window)
        if re.fullmatch(r'0x[0-9a-f]{1,16}',address) is None or re.fullmatch(r'[0-9a-f]{1,16}',sid) is None or pid<1:raise ValueError('invalid snapshot cache identity')
        return 'full-'+sid+'-'+str(pid)
    def read(self,path,bound):
        fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
        try:
            info=os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_uid!=os.getuid() or info.st_mode&0o077 or info.st_size>bound:raise ValueError('invalid private cache file')
            with os.fdopen(fd,'rb',closefd=False) as source:data=source.read(bound+1)
            if len(data)>bound or len(data)!=info.st_size:raise ValueError('cache file changed/truncated')
            after=os.fstat(fd)
            if (info.st_dev,info.st_ino,info.st_size,info.st_mtime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns):raise ValueError('cache file changed during read')
            return data
        finally:os.close(fd)
    @contextmanager
    def pair(self,stem,*,nonblocking=False):
        fd=os.open(self.root/'cache.lock',os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW|os.O_NONBLOCK,0o600)
        try:
            info=os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_uid!=os.getuid() or info.st_mode&0o077:raise ValueError('invalid private cache lock')
            fcntl.flock(fd,fcntl.LOCK_EX | (fcntl.LOCK_NB if nonblocking else 0))
            yield
        finally:os.close(fd)
    def validate(self,window,metadata,pixels):
        if (metadata.get('compositorSession')!=self.session or metadata.get('identity')!=list(key(window)) or metadata.get('clientSize')!=list(window['size'])
                or not metadata.get('whole') or not metadata.get('canonical')):raise ValueError('persistent cache identity/whole metadata mismatch')
        self.validate_snapshot(metadata,rectangle(window))
        if len(pixels)<33 or pixels[:8]!=b'\x89PNG\r\n\x1a\n' or pixels[12:16]!=b'IHDR':raise ValueError('invalid cached PNG header')
        width,height=struct.unpack('!II',pixels[16:24])
        if [width,height]!=metadata['pixels'] or not 0<width<=8192 or not 0<height<=8192 or pixels[24]!=8 or pixels[25] not in (2,6):raise ValueError('cached PNG dimensions/format mismatch')
        if hashlib.sha256(pixels).hexdigest()!=metadata.get('cacheDigest'):raise ValueError('persistent cache PNG digest mismatch')
    def write_atomic(self,path,data):
        temporary=self.root/('.cache-'+uuid.uuid4().hex+'.tmp')
        try:
            fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(fd,'wb') as output:output.write(data);output.flush();os.fsync(output.fileno())
            temporary.replace(path)
            directory=os.open(self.root,os.O_RDONLY|os.O_DIRECTORY)
            try:os.fsync(directory)
            finally:os.close(directory)
        finally:temporary.unlink(missing_ok=True)
    def publish(self,window,metadata,pixels):
        metadata=dict(metadata,compositorSession=self.session,cacheDigest=hashlib.sha256(pixels).hexdigest())
        self.validate(window,metadata,pixels)
        stem=self.stem(window)
        with self.pair(stem):
            destination=self.root/(stem+'-'+metadata['cacheDigest']+'.png')
            metadata['cacheFile']=destination.name
            old=None
            pointer=self.root/(stem+'.json')
            if pointer.exists():
                try:old=json.loads(self.read(pointer,1048576)).get('cacheFile')
                except (OSError,ValueError):pass
            if not destination.exists():self.write_atomic(destination,pixels)
            elif hashlib.sha256(self.read(destination,268435456)).hexdigest()!=metadata['cacheDigest']:
                raise ValueError('existing immutable cache PNG changed')
            # The single atomic pointer commit publishes a complete immutable
            # pair. Failure before this rename leaves the last valid pair live.
            self.write_atomic(pointer,json.dumps(metadata,separators=(',',':')).encode())
            if isinstance(old,str) and old!=destination.name and re.fullmatch(re.escape(stem)+r'-[0-9a-f]{64}\.png',old):
                (self.root/old).unlink(missing_ok=True)
    def prune(self,live_identities,*,complete,nonblocking=False):
        if complete is not True:raise ValueError('cache pruning requires complete live identity observation')
        live=set(live_identities)
        pattern=re.compile(r'full-([0-9a-f]{1,16})-([1-9][0-9]*)\.json')
        immutable=re.compile(r'full-[0-9a-f]{1,16}-[1-9][0-9]*-[0-9a-f]{64}\.png')
        scratch=re.compile(r'\.cache-[0-9a-f]{32}\.tmp')
        removed=[]
        with self.pair('janitor',nonblocking=nonblocking):
            referenced=set()
            for path in list(self.root.iterdir()):
                match=pattern.fullmatch(path.name)
                if not match:continue
                metadata=json.loads(self.read(path,1048576))
                identity=tuple(metadata.get('identity',[]))
                if (len(identity)!=3 or identity[1]!=match[1] or str(identity[2])!=match[2]
                        or metadata.get('compositorSession')!=self.session):
                    raise ValueError('cache metadata provenance invalid during pruning')
                cache_file=metadata.get('cacheFile','')
                expected=path.stem+'-'+str(metadata.get('cacheDigest'))+'.png'
                if cache_file!=expected:raise ValueError('cache pointer invalid during pruning')
                if identity in live:referenced.add(cache_file);continue
                path.unlink(missing_ok=True);removed.append(path)
            # The same global lock excludes every active publisher/reader. Only
            # strict own scratch/immutable names can be abandoned here.
            for path in list(self.root.iterdir()):
                if not (scratch.fullmatch(path.name) or immutable.fullmatch(path.name) and path.name not in referenced):continue
                info=path.lstat()
                if not stat.S_ISREG(info.st_mode) or info.st_uid!=os.getuid() or info.st_mode&0o077:continue
                path.unlink(missing_ok=True);removed.append(path)
        return removed
    def restore(self,window):
        stem=self.stem(window)
        with self.pair(stem):
            metadata=json.loads(self.read(self.root/(stem+'.json'),1048576))
            expected=stem+'-'+str(metadata.get('cacheDigest'))+'.png'
            if metadata.get('cacheFile')!=expected:raise ValueError('invalid immutable cache pointer')
            pixels=self.read(self.root/expected,268435456)
            self.validate(window,metadata,pixels)
            return metadata,pixels
