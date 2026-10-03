"""Owned family thumbnail generation; no native effects or launch on import.

The controller's preparation worker owns this synchronous operation. A helper
with uncertain group closure quarantines the pending sources and output folder.
"""
from contextlib import ExitStack
from copy import deepcopy
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import struct
import subprocess
import threading
import uuid
import zlib
from owned_commands import OwnedCommands
from scene_controller import key, rectangle

EPOCH=re.compile(r'[0-9a-f]{12}-[1-9][0-9]{0,14}')
ADDRESS=re.compile(r'0x[0-9a-f]+')
MAX_PNG=128*1024*1024

def file_identity(info):
    return (info.st_dev,info.st_ino,info.st_size,info.st_mtime_ns,info.st_ctime_ns)

def png_dimensions(data, *, complete=False):
    """Check all chunk CRCs; also validate complete bounded thumbnail scanlines."""
    if not data.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('PNG signature required')
    offset=8;header=None;compressed=[];ended=False
    while offset<len(data):
        if offset+12>len(data):raise ValueError('truncated PNG chunk')
        length=struct.unpack_from('!I',data,offset)[0];kind=data[offset+4:offset+8]
        end=offset+12+length
        if end>len(data):raise ValueError('truncated PNG payload')
        body=data[offset+8:end-4]
        if zlib.crc32(kind+body)&0xffffffff!=struct.unpack_from('!I',data,end-4)[0]:raise ValueError('PNG CRC differs')
        if header is None:
            if kind!=b'IHDR' or length!=13:raise ValueError('PNG header required')
            header=struct.unpack('!2I5B',body)
        elif kind==b'IHDR':raise ValueError('duplicate PNG header')
        if kind==b'IDAT':compressed.append(body)
        if kind==b'IEND':
            if length or end!=len(data):raise ValueError('PNG trailing material')
            ended=True;break
        offset=end
    if not header or not ended or not compressed:raise ValueError('complete PNG required')
    width,height,depth,color,compression,filtering,interlace=header
    depths={0:(1,2,4,8,16),2:(8,16),3:(1,2,4,8),4:(8,16),6:(8,16)}
    if not 0<width<=32768 or not 0<height<=32768 or depth not in depths.get(color,()) or compression or filtering or interlace not in (0,1):raise ValueError('invalid PNG header')
    if complete:
        if width>300 or height>180 or interlace:raise ValueError('bounded noninterlaced thumbnail required')
        channels={0:1,2:3,3:1,4:2,6:4}[color];stride=(width*channels*depth+7)//8+1
        limit=stride*height
        decoder=zlib.decompressobj();decoded=decoder.decompress(b''.join(compressed),limit+1)
        if (len(decoded)!=limit or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail
                or any(decoded[i*stride]>4 for i in range(height))):raise ValueError('invalid PNG scanlines')
    return width,height

class PinnedPNG:
    def __init__(self,path,*,digest=None,dimensions=None,complete=False):
        self.path=Path(path);self.fd=os.open(self.path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
        try:
            before=os.fstat(self.fd)
            if not stat.S_ISREG(before.st_mode) or before.st_uid!=os.getuid() or before.st_size>MAX_PNG or before.st_size<33:raise ValueError('owned bounded PNG file required')
            self.identity=file_identity(before);self.data=os.pread(self.fd,before.st_size+1,0)
            self.digest=hashlib.sha256(self.data).hexdigest()
            self.dimensions=png_dimensions(self.data,complete=complete)
            if digest is not None and self.digest!=digest:raise ValueError('source PNG digest changed')
            if dimensions is not None and self.dimensions!=tuple(dimensions):raise ValueError('PNG dimensions differ')
            self.check()
        except BaseException:self.close();raise
    def check(self):
        if file_identity(os.fstat(self.fd))!=self.identity or file_identity(self.path.lstat())!=self.identity:raise ValueError('source PNG inode changed')
        if hashlib.sha256(os.pread(self.fd,self.identity[2]+1,0)).hexdigest()!=self.digest:raise ValueError('source PNG bytes changed')
    def close(self):
        if self.fd is not None:os.close(self.fd);self.fd=None
    def __enter__(self):return self
    def __exit__(self,*args):self.close()

def crop_geometry(window,metadata):
    scale=metadata['pixels'][0]/metadata['rect']['width'];insets=metadata['insets']
    width,height=(round(v*scale) for v in window['size'])
    x,y=(round(insets[k]*scale) for k in ('left','top'))
    if min(width,height)<1 or min(x,y)<0 or x+width>metadata['pixels'][0] or y+height>metadata['pixels'][1]:raise ValueError('exact crop exceeds atlas')
    ratio=min(1,300/width,180/height)
    expected=(max(1,math.floor(width*ratio+.5)),max(1,math.floor(height*ratio+.5)))
    return f'{width}x{height}+{x}+{y}',expected

class BatchPreviews:
    def __init__(self,root,preview,commands):
        if not isinstance(commands,OwnedCommands):raise ValueError('batch previews require sealed owned commands')
        self.root=Path(root);self.preview=Path(preview);self.commands=commands
        self.pending={};self.active=False;self.quarantined=False;self.retained_folder=None
        self.lock=threading.RLock();self.active_epochs=set()
        self.staging={};self.staging_serial=0
    def stage(self,window,epoch,image,metadata):
        image=Path(image)
        if image!=self.root/(epoch+'.png') or not ADDRESS.fullmatch(window['address']):raise ValueError('exact pending crop path/identity required')
        crop,dimensions=crop_geometry(window,metadata)
        snapshot={'window':deepcopy(window),'metadata':deepcopy(metadata),'path':image,
            'crop':crop,'dimensions':dimensions}
        with self.lock:
            if (self.active or self.quarantined or not EPOCH.fullmatch(epoch) or epoch in self.pending
                    or epoch in self.staging or len(self.pending)+len(self.staging)>=64):raise ValueError('pending crop lifecycle unavailable')
            self.staging_serial+=1
            reservation={'serial':self.staging_serial,'snapshot':snapshot}
            self.staging[epoch]=reservation
        try:
            # All material I/O, validation, hashing and descriptor closure occur
            # outside lifecycle/receipt locks. Exact reservation retains epoch.
            with PinnedPNG(image,dimensions=snapshot['metadata']['pixels']) as pinned:
                material={**snapshot,'digest':pinned.digest,'inode':pinned.identity}
            with self.lock:
                if self.staging.get(epoch) is not reservation:
                    raise ValueError('exact staging reservation changed')
                if self.active or self.quarantined or epoch in self.pending:
                    raise ValueError('staging publication lifecycle unavailable')
                self.pending[epoch]=material
                del self.staging[epoch]
        except BaseException:
            with self.lock:
                if self.staging.get(epoch) is reservation:
                    del self.staging[epoch]
                else:
                    self.quarantined=True;self.active_epochs.add(epoch)
            raise
    def discard(self,epoch):
        with self.lock:
            self.require_releasable({epoch});self.pending.pop(epoch,None)
    def require_releasable(self,epochs):
        if set(epochs)&self.staging.keys():raise ValueError('unfinished crop staging retains capture material')
        if (self.active or self.quarantined) and set(epochs)&self.active_epochs:raise ValueError('unfinished thumbnail helper retains capture material')
    def require_idle(self):
        if self.active or self.quarantined:raise ValueError('unfinished thumbnail helper retains capture material')
    def require_disposable(self):
        with self.lock:
            self.require_idle()
            if self.staging:raise ValueError('staging crops prevent normal disposal')
            if self.pending:raise ValueError('pending crops prevent normal disposal')
    def _closed(self):
        keeper=self.commands.keeper
        with keeper.lock:
            keeper.verify()
            return not any(row.get('actor')==self.commands.actor for row in keeper.jobs.values())
    @staticmethod
    def check_family(members,clients):
        live={key(w):w for w in clients if w.get('mapped',True)}
        if len(live)!=len([w for w in clients if w.get('mapped',True)]):raise ValueError('ambiguous current native identities')
        for member in members:
            current=live.get(key(member))
            if current is None or rectangle(current)!=rectangle(member):raise ValueError('native identity or geometry changed during batch')
    @staticmethod
    def write_exclusive(path,data):
        with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb') as output:
            output.write(data);output.flush();os.fsync(output.fileno())
    def _reserve(self,sources,members):
        self.require_idle()
        if self.staging:raise ValueError('unfinished staging crop prevents thumbnail launch')
        if not 1<=len(sources)==len(members)<=64 or len({key(w) for w in members})!=len(members):raise ValueError('complete unique capture family required')
        rows=[]
        for source,member in zip(sources,members,strict=True):
            if str(source.get('stableId'))!=str(member['stableId']) or source.get('pid')!=member['pid'] or source.get('nativeRect')!=rectangle(member):raise ValueError('capture lease identity differs')
            epoch=source.get('captureEpoch');row=self.pending.get(epoch)
            if row is not None:
                if (key(row['window'])!=key(member) or row['path']!=Path(source.get('path',''))
                        or row['digest']!=source.get('digest') or rectangle(row['window'])!=rectangle(member)):raise ValueError('pending crop differs from returned lease')
                rows.append((epoch,row))
            elif member.get('workspace',{}).get('name')!='special:win-minimized':raise ValueError('visible capture lacks pending crop')
        self.active=bool(rows);self.active_epochs={epoch for epoch,_ in rows}
        return rows
    def finish(self,sources,members,*,clients,current,reservation_lock):
        with self.lock:rows=self._reserve(sources,members)
        if not rows:return
        folder=None;generated=[]
        try:
            with reservation_lock:
                if not current():raise ValueError('batch receipt was superseded')
            if not self._closed():raise ValueError('outstanding actor helper prevents thumbnail launch')
            self.preview.mkdir(mode=0o700,parents=True,exist_ok=True)
            info=self.preview.lstat()
            if not stat.S_ISDIR(info.st_mode) or info.st_uid!=os.getuid() or info.st_mode&0o077:raise ValueError('private preview directory required')
            folder=self.preview/('.motion-batch-'+uuid.uuid4().hex);folder.mkdir(mode=0o700)
            with ExitStack() as stack:
                for address in sorted(row['window']['address'] for _,row in rows):
                    fd=os.open(self.preview/(address+'.lock'),os.O_WRONLY|os.O_CREAT|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
                    stack.callback(os.close,fd)
                    lock_info=os.fstat(fd)
                    if not stat.S_ISREG(lock_info.st_mode) or lock_info.st_uid!=os.getuid():raise ValueError('exact preview lock required')
                    fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
                self.check_family(members,clients())
                inputs=[];argv=['magick','-respect-parentheses']
                for index,(epoch,row) in enumerate(rows):
                    pinned=stack.enter_context(PinnedPNG(row['path'],digest=row['digest'],dimensions=row['metadata']['pixels']))
                    if pinned.identity!=row['inode']:raise ValueError('staged source PNG inode changed')
                    inputs.append(pinned);output=folder/(epoch+'.png');generated.append(output)
                    argv+=['(',f'png:/proc/self/fd/{pinned.fd}','-crop',row['crop'],'+repage','-thumbnail','300x180>',')']
                    argv+=['-write',str(output),'+delete'] if index<len(rows)-1 else [str(output)]
                try:
                    result=self.commands.run(argv,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                        timeout=1,pass_fds=tuple(p.fd for p in inputs))
                    if type(result.returncode) is not int or result.returncode!=0:raise ValueError('thumbnail helper did not complete normally')
                    if not self._closed():raise ValueError('thumbnail helper group closure unavailable')
                except BaseException:
                    try:closed=self._closed()
                    except BaseException:closed=False
                    if not closed:
                        with self.lock:self.quarantined=True;self.retained_folder=folder
                    raise
                for pinned in inputs:pinned.check()
                pixels=[]
                for (_,row),output in zip(rows,generated,strict=True):
                    with PinnedPNG(output,dimensions=row['dimensions'],complete=True) as pinned:pixels.append(pinned.data)
                self.check_family(members,clients())
                # No helper wait or staged-file fsync holds the receipt lock.
                publication=[]
                for (epoch,row),data in zip(rows,pixels,strict=True):
                    window=row['window'];address=window['address']
                    for slot in (0,1):
                        path=folder/(epoch+'-'+str(slot)+'.tmp');self.write_exclusive(path,data)
                        publication.append((path,self.preview/(address+'-'+str(slot)+'.png')))
                    path=folder/(epoch+'.json.tmp')
                    self.write_exclusive(path,(json.dumps({'pid':window['pid'],'stableId':window['stableId']},separators=(',',':'))+'\n').encode())
                    publication.append((path,self.preview/(address+'.json')))
                with reservation_lock:
                    if not current():raise ValueError('batch receipt was superseded before preview publication')
                    for pinned in inputs:pinned.check()
                    for path,destination in publication:path.replace(destination)
                    with self.lock:
                        for epoch,_ in rows:self.pending.pop(epoch)
        finally:
            with self.lock:
                self.active=False
                if not self.quarantined:self.active_epochs=set()
            if folder is not None and not self.quarantined:
                for path in folder.iterdir():path.unlink()
                folder.rmdir()
