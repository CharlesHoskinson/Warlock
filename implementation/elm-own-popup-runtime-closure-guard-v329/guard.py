"""Read-only exact321 runtime checks. No host/menu authentication or effect grant."""
import hashlib,json,math,os,re,stat,time
from pathlib import Path

class Refused(ValueError): pass
TUPLE=Path('/home/hoskinson/omarchy-windows-parity/implementation/elm-own-popup-native-tuple-plan-v321/runtime')
DESCRIPTOR_SHA='c36b32d7f621239cd9e4ba205fa5a4eda91daf8466a4c1fec03a7b0f5e3ce439'
def require(value,message):
    if not value: raise Refused(message)
def remaining(deadline):
    require(type(deadline) is float and math.isfinite(deadline) and time.monotonic()<deadline,'original deadline exhausted')
def fingerprint(path,deadline,*,retain_limit=None):
    h=hashlib.sha256();chunks=[];total=0
    remaining(deadline)
    try:fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NONBLOCK|os.O_NOFOLLOW)
    except OSError as e:raise Refused('pinned file open refused') from e
    try:
        before=os.fstat(fd);require(stat.S_ISREG(before.st_mode),'not regular file')
        f=os.fdopen(fd,'rb')
    except BaseException:
        os.close(fd);raise
    with f:
        while True:
            remaining(deadline);b=f.read(1048576)
            if not b:break
            h.update(b)
            if retain_limit is not None:
                total+=len(b);require(total<=retain_limit,'pinned metadata byte bound');chunks.append(b)
        after=os.fstat(f.fileno())
        require((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'file changed during hash')
        linked=Path(path).stat(follow_symlinks=False)
        require((linked.st_dev,linked.st_ino,linked.st_size,linked.st_mtime_ns,linked.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'file path replaced during hash')
    remaining(deadline)
    return h.hexdigest(),(os.major(after.st_dev),os.minor(after.st_dev),after.st_ino),b''.join(chunks)
def digest(path,deadline):return fingerprint(path,deadline)[0]
def pinned(path,expected,deadline):
    actual,file_identity,_=fingerprint(path,deadline)
    require(actual==expected,'source/runtime file changed: '+str(path));return file_identity
def read_pinned(path,expected,deadline,*,limit=1048576):
    actual,_,raw=fingerprint(path,deadline,retain_limit=limit)
    require(actual==expected,'pinned metadata changed: '+str(path));return raw
def verify_tuple(*,deadline):
    descriptor=TUPLE/'native-build-report.json'
    d=json.loads(read_pinned(descriptor,DESCRIPTOR_SHA,deadline));closure=Path(d['linkClosureReport'])
    c=json.loads(read_pinned(closure,d['linkClosureReportSHA256'],deadline));require(c['passed'] and not any(c['missingSymbols'].values()),'runtime symbol closure failed')
    pinned('/etc/ld.so.cache',c['currentLinkerCache']['sha256'],deadline)
    for p,row in c['tools'].items():pinned(p,row['sha256'],deadline)
    for p,h in c['libraries'].items():pinned(p,h,deadline)
    artifacts={d['binary']:d['sha256'],d['plugin']['path']:d['plugin']['sha256'],d['observer']['path']:d['observer']['sha256']}
    aq=[p for p in c['libraries'] if Path(p).name.startswith('libaquamarine.so')]
    require(len(aq)==1,'ambiguous Aquamarine lookup');artifacts[aq[0]]=c['libraries'][aq[0]]
    for p,h in artifacts.items():pinned(p,h,deadline)
    return {'artifacts':artifacts,'libraries':c['libraries'],'descriptorSHA256':DESCRIPTOR_SHA,'authenticatedHost':False,'nativeAcceptance':False}

def process_identity(raw,*,pid):
    require(type(pid) is int and 1<pid<=2**31-1,'invalid child PID')
    require(type(raw) is str and len(raw)<=65536,'process stat bound')
    end=raw.rfind(')');require(end>=0 and raw.startswith(str(pid)+' ('),'process stat PID mismatch')
    tail=raw[end+2:].split();require(len(tail)>=20 and tail[0] in ('R','S','D','T','t','W','P','I'),'dead/unknown/incomplete child')
    require(1<=len(tail[19])<=20 and tail[19].isascii() and tail[19].isdecimal() and 0<int(tail[19])<=2**64-1,'invalid process start')
    return int(tail[19])

def parse_maps(raw):
    require(type(raw) is str and len(raw.encode())<=4194304,'process maps bound')
    lines=raw.splitlines();require(len(lines)<=16384,'process maps row bound')
    result={}
    for line in lines:
        row=line.split(None,5);require(len(row)>=5,'malformed mapping')
        require(re.fullmatch(r'[0-9a-f]{1,16}-[0-9a-f]{1,16}',row[0]) and re.fullmatch(r'[r-][w-][x-][ps]',row[1]) and re.fullmatch(r'[0-9a-f]{1,16}',row[2]) and re.fullmatch(r'[0-9a-f]{1,8}:[0-9a-f]{1,8}',row[3]) and 1<=len(row[4])<=20 and row[4].isascii() and row[4].isdecimal() and int(row[4])<=2**64-1,'malformed mapping fields')
        lo,hi=(int(v,16) for v in row[0].split('-'));require(lo<hi,'invalid mapping range')
        if len(row)<6 or not row[5].startswith('/'):continue
        name=re.sub(r'\\([0-7]{3})',lambda m:chr(int(m[1],8)),row[5])
        require('\x00' not in name,'NUL mapping path')
        dev=tuple(int(v,16) for v in row[3].split(':'));identity=(*dev,int(row[4]))
        require(identity[2]>0,'file mapping missing inode')
        require(name not in result or result[name]==identity,'mapping inode changed')
        result[name]=identity
    return result

def match_maps(mapped,required,identities):
    for p in required:
        require(p in mapped,'required runtime artifact absent: '+p)
        require(mapped[p]==identities[p],'mapped inode differs: '+p)
        require(not any(Path(q.removesuffix(' (deleted)')).name==Path(p).name and q!=p for q in mapped),'alternate/deleted runtime artifact: '+p)
    return True

def map_identity(path,disk_identity,mountinfo):
    """Btrfs stat uses subvolume anon_dev; proc maps uses superblock s_dev."""
    require(type(mountinfo) is str and len(mountinfo.encode())<=1048576,'mountinfo bound')
    require(len(mountinfo.splitlines())<=4096,'mountinfo row bound')
    choices=[];path=Path(path)
    for line in mountinfo.splitlines():
        row=line.split();require(len(row)>=10 and '-' in row,'malformed mountinfo')
        sep=row.index('-');require(sep>=6 and len(row)>sep+3,'malformed mountinfo separator')
        mount=Path(re.sub(r'\\([0-7]{3})',lambda m:chr(int(m[1],8)),row[4]))
        require(mount.is_absolute() and re.fullmatch(r'[0-9]{1,10}:[0-9]{1,10}',row[2]) and all(int(v)<=2**32-1 for v in row[2].split(':')),'malformed mountinfo identity')
        if path.is_relative_to(mount):choices.append((len(mount.parts),mount,row[2],row[sep+1]))
    require(bool(choices),'path has no owning mount')
    depth=max(c[0] for c in choices);selected=[c for c in choices if c[0]==depth]
    require(len(selected)==1,'ambiguous owning mount')
    _,mount,device,fs=selected[0]
    if fs!='btrfs':return disk_identity
    s=mount.stat();require((os.major(s.st_dev),os.minor(s.st_dev))==disk_identity[:2],'unmounted Btrfs subvolume cannot be joined')
    return (*tuple(int(v) for v in device.split(':')),disk_identity[2])

def read_text_bounded(path,limit):
    with Path(path).open('rb') as f:raw=f.read(limit+1)
    require(len(raw)<=limit,'procfs read bound')
    try:return raw.decode('utf-8',errors='strict')
    except UnicodeError as e:raise Refused('procfs UTF8') from e

def verify_process(*,pid,start,tuple_evidence,deadline):
    """Call after BOTH plugins loaded; bracket reads with original child PID/start."""
    require(type(start) is int and start>0,'invalid expected start')
    remaining(deadline);proc=Path('/proc')/str(pid)
    namespace=(Path('/proc/self/ns/mnt').stat().st_dev,Path('/proc/self/ns/mnt').stat().st_ino)
    mountinfo=read_text_bounded('/proc/self/mountinfo',1048576)
    def live():
        remaining(deadline);require(proc.stat().st_uid==os.getuid(),'foreign process UID')
        s=(proc/'ns/mnt').stat();require((s.st_dev,s.st_ino)==namespace,'child mount namespace differs')
        require(process_identity(read_text_bounded(proc/'stat',65536),pid=pid)==start,'child incarnation changed')
    live()
    with (proc/'maps').open() as f:raw=f.read(4194305)
    mapped=parse_maps(raw);required=tuple_evidence['artifacts'];identities={}
    for p,h in required.items():
        identities[p]=map_identity(p,pinned(p,h,deadline),mountinfo)
    match_maps(mapped,required,identities)
    binary=next(iter(required));s=(proc/'exe').stat()
    require(map_identity(binary,(os.major(s.st_dev),os.minor(s.st_dev),s.st_ino),mountinfo)==identities[binary],'child executable differs')
    library_identities={p:map_identity(p,pinned(p,h,deadline),mountinfo) for p,h in tuple_evidence['libraries'].items()}
    match_maps(mapped,tuple_evidence['libraries'],library_identities)
    live();require(read_text_bounded('/proc/self/mountinfo',1048576)==mountinfo,'mount topology changed');remaining(deadline)
    return {'pid':pid,'start':start,'requiredArtifacts':list(required),'mappedLibraryCount':len(tuple_evidence['libraries']),'mapsSHA256':hashlib.sha256(raw.encode()).hexdigest(),'authenticatedHost':False,'nativeAcceptance':False,'scope':'Bracketed diagnostic process mapping; no atomic compositor/host/menu proof'}
