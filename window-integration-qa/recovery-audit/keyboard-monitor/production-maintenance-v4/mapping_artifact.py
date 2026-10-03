"""Calibrate kernel backing identity from a pinned artifact FD, without dlopen."""
from contextlib import contextmanager
from pathlib import Path
import ctypes,hashlib,mmap,os,stat

class MappingRefused(RuntimeError):pass

def witness(row):
    return (row.st_dev,row.st_ino,row.st_uid,row.st_gid,row.st_mode,
            row.st_size,row.st_mtime_ns,row.st_ctime_ns)

def descriptor_hash(fd,size):
    digest=hashlib.sha256();offset=0
    while offset<size:
        block=os.pread(fd,min(1048576,size-offset),offset)
        if not block:raise MappingRefused('artifact descriptor truncated')
        digest.update(block);offset+=len(block)
    if os.pread(fd,1,size):raise MappingRefused('artifact descriptor grew')
    return digest.hexdigest()

def verify_pinned(fd,path,initial,expected_hash):
    before=os.fstat(fd);named=path.lstat()
    if not stat.S_ISREG(before.st_mode) or not stat.S_ISREG(named.st_mode) or before.st_uid!=os.getuid() or before.st_mode&0o022:
        raise MappingRefused('unsafe pinned artifact ownership/mode')
    if witness(before)!=initial or witness(named)!=initial:
        raise MappingRefused('pinned artifact descriptor/path identity changed')
    if path.resolve()!=path or Path(f'/proc/self/fd/{fd}').resolve()!=path:
        raise MappingRefused('pinned artifact canonical FD/path changed')
    if descriptor_hash(fd,before.st_size)!=expected_hash:
        raise MappingRefused('pinned artifact bytes changed')
    if witness(os.fstat(fd))!=initial or witness(path.lstat())!=initial:
        raise MappingRefused('pinned artifact changed during hashing')

def parse_mapping(line):
    parts=line.split(maxsplit=5)
    if len(parts)!=6:return None
    try:
        first,last=(int(value,16) for value in parts[0].split('-'))
        major,minor=(int(value,16) for value in parts[3].split(':'))
        offset=int(parts[2],16);inode=int(parts[4])
    except ValueError as error:raise MappingRefused('malformed kernel mapping') from error
    return dict(first=first,last=last,permissions=parts[1],offset=offset,
                device=os.makedev(major,minor),inode=inode,path=parts[5])

def exact_remote_maps(text,path,calibration):
    matches=[]
    for line in text.splitlines():
        parts=line.split(maxsplit=5)
        if len(parts)!=6 or parts[5] not in (str(path),str(path)+' (deleted)'):continue
        row=parse_mapping(line)
        if row['path']!=str(path) or (row['device'],row['inode'])!=(calibration['device'],calibration['inode']):
            raise MappingRefused('loaded mapping identity differs from calibrated backing')
        matches.append(row)
    if not matches:raise MappingRefused('exact loaded artifact mapping missing')
    return matches

@contextmanager
def calibrated_artifact(path,expected_hash):
    path=Path(path).absolute()
    named=path.lstat();initial=witness(named)
    if path.resolve()!=path or not stat.S_ISREG(named.st_mode) or not 1<=named.st_size<=536870912:
        raise MappingRefused('exact bounded canonical artifact required')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK)
    try:
        verify_pinned(fd,path,initial,expected_hash)
        # ACCESS_COPY supplies a Python buffer address with private COW memory.
        # This map never has executable permissions and never calls artifact code.
        with mmap.mmap(fd,named.st_size,access=mmap.ACCESS_COPY) as mapped:
            buffer=ctypes.c_char.from_buffer(mapped)
            address=ctypes.addressof(buffer);del buffer
            matches=[]
            for line in Path('/proc/self/maps').read_text().splitlines():
                row=parse_mapping(line)
                if row and row['first']<=address<row['last']:matches.append(row)
            if len(matches)!=1:raise MappingRefused('unique actual buffer mapping required')
            row=matches[0]
            if row['path']!=str(path) or row['inode']!=named.st_ino or row['offset']!=0 or 'x' in row['permissions'] or not row['permissions'].endswith('p'):
                raise MappingRefused('self buffer mapping backing differs')
            verify_pinned(fd,path,initial,expected_hash)
            calibration=dict(device=row['device'],inode=row['inode'],statDevice=named.st_dev,
                statInode=named.st_ino,exactPath=str(path),bufferAddress=address,
                selfMapping=row,sha256=expected_hash,fdPinned=True,nativeCodeExecuted=False)
            yield calibration
            verify_pinned(fd,path,initial,expected_hash)
    finally:os.close(fd)
