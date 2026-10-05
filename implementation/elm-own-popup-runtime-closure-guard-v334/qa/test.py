import copy,hashlib,importlib.util,json,mmap,os,resource,shutil,subprocess,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def exercise(path,record_dir=None):
    spec=importlib.util.spec_from_file_location('guard',path);g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
    checks=[]
    def reject(name,f):
        try:f()
        except g.Refused:checks.append(name);return
        raise AssertionError('unsafe acceptance: '+name)
    maps=g.parse_maps(Path('/proc/self/maps').read_text());binary=str(Path('/proc/self/exe').resolve())
    libs=[p for p in maps if Path(p).name.startswith('libc.so')];assert len(libs)==1
    required={binary:sha(binary),libs[0]:sha(libs[0])}
    mountinfo=Path('/proc/self/mountinfo').read_text()
    identity={p:g.map_identity(p,(os.major(Path(p).stat().st_dev),os.minor(Path(p).stat().st_dev),Path(p).stat().st_ino),mountinfo) for p in required}
    g.match_maps(maps,required,identity);checks.append('actual self ELF/libc map identity')
    start=g.process_identity(Path('/proc/self/stat').read_text(),pid=os.getpid())
    evidence={'artifacts':required,'libraries':{libs[0]:required[libs[0]]}}
    result=g.verify_process(pid=os.getpid(),start=start,tuple_evidence=evidence,deadline=time.monotonic()+5.0)
    assert not result['authenticatedHost'] and not result['nativeAcceptance'];checks.append('actual self process bracket never native claim')
    descriptors=[];buffers=[]
    try:
        for _ in range(2):
            fd=os.memfd_create('guard334-same-label',os.MFD_CLOEXEC);descriptors.append(fd);os.ftruncate(fd,4096);buffers.append(mmap.mmap(fd,4096))
        raw=Path('/proc/self/maps').read_text();multiple=g.parse_maps(raw)
        name='/memfd:guard334-same-label (deleted)';assert len(multiple[name])==2
        observed=g.verify_process(pid=os.getpid(),start=start,tuple_evidence=evidence,deadline=time.monotonic()+5.0)
        assert len(observed['additionalAmbiguousMappings'][name])==2
        if record_dir is not None:
            (record_dir/'actual-memfd-maps.txt').write_text('\n'.join(l for l in raw.splitlines() if name in l)+'\n')
            (record_dir/'actual-memfd-observation.json').write_text(json.dumps(observed,indent=2)+'\n')
        checks.append('actual two distinct memfd identities same label accepted outside required tuple')
    finally:
        for b in buffers:b.close()
        for fd in descriptors:os.close(fd)
    reject('wrong start',lambda:g.verify_process(pid=os.getpid(),start=start+1,tuple_evidence=evidence,deadline=time.monotonic()+5.0))
    for bad_pid in [True,'../self',2**31]:
        reject('typed early PID '+str(bad_pid),lambda bad_pid=bad_pid:g.verify_process(pid=bad_pid,start=start,tuple_evidence=evidence,deadline=time.monotonic()+5.0))
    for bad_start in [True,2**64]:
        reject('typed early start '+str(bad_start),lambda bad_start=bad_start:g.verify_process(pid=os.getpid(),start=bad_start,tuple_evidence=evidence,deadline=time.monotonic()+5.0))
    reject('wrong artifact digest',lambda:g.pinned(binary,'0'*64,time.monotonic()+5.0))
    reject('expired deadline',lambda:g.pinned(binary,required[binary],time.monotonic()-1.0))
    raw=g.read_pinned(binary,required[binary],time.monotonic()+5.0);assert hashlib.sha256(raw).hexdigest()==required[binary];checks.append('parse bytes are hashed fd bytes')
    reject('bounded pinned metadata',lambda:g.read_pinned(binary,required[binary],time.monotonic()+5.0,limit=1))
    with tempfile.TemporaryDirectory(prefix='guard326-') as temporary:
        fifo=Path(temporary)/'fifo';os.mkfifo(fifo)
        reject('FIFO open refuses without blocking',lambda:g.pinned(fifo,'0'*64,time.monotonic()+0.5))
        symlink=Path(temporary)/'symlink';symlink.symlink_to(binary)
        reject('symlink pinned file refuses',lambda:g.pinned(symlink,required[binary],time.monotonic()+0.5))
        reject('directory pinned file refuses',lambda:g.pinned(temporary,'0'*64,time.monotonic()+0.5))
        extra=Path(temporary)/Path(libs[0]).name;shutil.copy2(libs[0],extra)
        with extra.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as mapping:
            assert len(mapping)>0
            only_binary={'artifacts':{binary:required[binary]},'libraries':evidence['libraries']}
            reject('actual alternate lookup library mmap',lambda:g.verify_process(pid=os.getpid(),start=start,tuple_evidence=only_binary,deadline=time.monotonic()+5.0))
    bad=copy.deepcopy(maps);del bad[binary];reject('missing mapped binary',lambda:g.match_maps(bad,required,identity))
    bad=copy.deepcopy(maps);bad[binary]=frozenset(((identity[binary][0],identity[binary][1],identity[binary][2]+1),));reject('wrong mapped inode',lambda:g.match_maps(bad,required,identity))
    bad=copy.deepcopy(maps);bad[binary]=frozenset(((identity[binary][0],identity[binary][1]+1,identity[binary][2]),));reject('wrong mapped device',lambda:g.match_maps(bad,required,identity))
    bad=copy.deepcopy(maps);bad[binary]=maps[binary]|frozenset(((identity[binary][0],identity[binary][1],identity[binary][2]+1),));reject('ambiguous required artifact mapping',lambda:g.match_maps(bad,required,identity))
    bad=copy.deepcopy(maps);bad['/other/'+Path(binary).name]=identity[binary];reject('alternate binary',lambda:g.match_maps(bad,required,identity))
    bad=copy.deepcopy(maps);bad[binary+' (deleted)']=identity[binary];reject('deleted binary alternate',lambda:g.match_maps(bad,required,identity))
    for name,raw in [('oversize',' '*4194305),('malformed','junk'),('bad permissions','100-200 rwqq 0 00:01 1 /tmp/a'),('no inode','100-200 r-xp 0 00:01 0 /tmp/a')]:
        reject(name,lambda raw=raw:g.parse_maps(raw))
    parsed=g.parse_maps(r'100-200 r-xp 0 00:01 1 /tmp/a\040b');assert '/tmp/a b' in parsed;checks.append('escaped map pathname')
    statline=Path('/proc/self/stat').read_text();reject('stat wrong PID',lambda:g.process_identity(statline,pid=os.getpid()+1))
    reject('boolean PID',lambda:g.process_identity(statline,pid=True))
    tail=statline[statline.rfind(')')+2:].split()
    assert g.process_identity(str(os.getpid())+' (a)b)c) '+' '.join(tail),pid=os.getpid())==start;checks.append('parentheses process name positive')
    reject('mountinfo malformed',lambda:g.map_identity(binary,identity[binary],'junk'))
    reject('mountinfo oversized',lambda:g.map_identity(binary,identity[binary],' '*1048577))
    reject('mountinfo no root',lambda:g.map_identity(binary,identity[binary],''))
    rootline=next(l for l in mountinfo.splitlines() if l.split()[4]=='/')
    reject('ambiguous mount root',lambda:g.map_identity(binary,identity[binary],mountinfo+'\n'+rootline))
    reject('unjoined btrfs subvolume',lambda:g.map_identity(binary,(0,0,identity[binary][2]),mountinfo))
    tail[0]='Z'
    reject('zombie child',lambda:g.process_identity(str(os.getpid())+' (a)b) '+' '.join(tail),pid=os.getpid()))
    tail[0]='unknown';reject('unknown child state',lambda:g.process_identity(str(os.getpid())+' (a) '+' '.join(tail),pid=os.getpid()))
    tail[0]='R';tail[19]='9'*5000;reject('oversize process start',lambda:g.process_identity(str(os.getpid())+' (a) '+' '.join(tail),pid=os.getpid()))
    reject('oversize map inode',lambda:g.parse_maps('100-200 r-xp 0 00:01 '+'9'*5000+' /tmp/a'))
    reject('oversize map device',lambda:g.parse_maps('100-200 r-xp 0 '+'f'*5000+':01 1 /tmp/a'))
    reject('inverted mapping range',lambda:g.parse_maps('200-100 r-xp 0 00:01 1 /tmp/a'))
    reject('bounded procfs read',lambda:g.read_text_bounded('/proc/self/stat',1))
    return checks
if len(sys.argv)==3 and sys.argv[1]=='--exercise':
    print(json.dumps(exercise(Path(sys.argv[2]))));raise SystemExit(0)
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('test-'+str(time.time_ns()));OUT.mkdir()
r={'passed':False,'nativeAcceptance':False,'scope':'Actual procfs self ELF/libc plus synthetic hostile maps; no native compositor/plugin load','mutants':[]}
try:
    for p in [ROOT/'guard.py',Path(__file__)]:shutil.copy2(p,OUT/p.name)
    r['inputs']={str(p):sha(p) for p in [ROOT/'guard.py',Path(__file__)]};r['checks']=exercise(OUT/'guard.py',record_dir=OUT)
    source=(OUT/'guard.py').read_text()
    for name,old,new in [('digest-bypass',"require(actual==expected,'source/runtime file changed: '+str(path))","require(True,'source/runtime file changed: '+str(path))"),('start-bypass',"process_identity(read_text_bounded(proc/'stat',65536),pid=pid)==start",'True'),('inode-bypass','mapped[p]==frozenset((identities[p],))','True'),('alias-bypass',"not any(Path(q.removesuffix(' (deleted)')).name==Path(p).name and q!=p for q in mapped)",'True'),('library-alias-bypass',"match_maps(mapped,tuple_evidence['libraries'],library_identities)",'pass')]:
        assert source.count(old)==1;p=OUT/(name+'.py');p.write_text(source.replace(old,new))
        child=subprocess.run([sys.executable,'-B',str(OUT/'test.py'),'--exercise',str(p)],capture_output=True,timeout=30)
        (OUT/(name+'.stdout')).write_bytes(child.stdout);(OUT/(name+'.stderr')).write_bytes(child.stderr)
        assert child.returncode!=0 and b'unsafe acceptance:' in child.stderr,(name,child.stderr)
        r['mutants'].append({'name':name,'killed':True,'exitCode':child.returncode})
    spec=importlib.util.spec_from_file_location('guard',OUT/'guard.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
    r['tuple']=g.verify_tuple(deadline=time.monotonic()+60.0)
    for p,h in r['inputs'].items():assert sha(p)==h
    r['passed']=True
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'checks':len(r.get('checks',[])),'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
