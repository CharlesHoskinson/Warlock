import copy,hashlib,importlib.util,json,os,resource,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def exercise(path):
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
    reject('wrong start',lambda:g.verify_process(pid=os.getpid(),start=start+1,tuple_evidence=evidence,deadline=time.monotonic()+5.0))
    reject('wrong artifact digest',lambda:g.pinned(binary,'0'*64,time.monotonic()+5.0))
    reject('expired deadline',lambda:g.pinned(binary,required[binary],time.monotonic()-1.0))
    bad=copy.deepcopy(maps);del bad[binary];reject('missing mapped binary',lambda:g.match_maps(bad,required,identity))
    bad=copy.deepcopy(maps);bad[binary]=(identity[binary][0],identity[binary][1],identity[binary][2]+1);reject('wrong mapped inode',lambda:g.match_maps(bad,required,identity))
    bad=copy.deepcopy(maps);bad['/other/'+Path(binary).name]=identity[binary];reject('alternate binary',lambda:g.match_maps(bad,required,identity))
    bad=copy.deepcopy(maps);bad[binary+' (deleted)']=identity[binary];reject('deleted binary alternate',lambda:g.match_maps(bad,required,identity))
    for name,raw in [('oversize',' '*4194305),('malformed','junk'),('bad permissions','100-200 rwqq 0 00:01 1 /tmp/a'),('no inode','100-200 r-xp 0 00:01 0 /tmp/a'),('conflicting inode','100-200 r-xp 0 00:01 1 /tmp/a\n200-300 r--p 0 00:01 2 /tmp/a')]:
        reject(name,lambda raw=raw:g.parse_maps(raw))
    parsed=g.parse_maps(r'100-200 r-xp 0 00:01 1 /tmp/a\040b');assert '/tmp/a b' in parsed;checks.append('escaped map pathname')
    statline=Path('/proc/self/stat').read_text();reject('stat wrong PID',lambda:g.process_identity(statline,pid=os.getpid()+1))
    reject('boolean PID',lambda:g.process_identity(statline,pid=True))
    tail=statline[statline.rfind(')')+2:].split();tail[0]='Z'
    reject('zombie child',lambda:g.process_identity(str(os.getpid())+' (a)b) '+' '.join(tail),pid=os.getpid()))
    return checks
if len(sys.argv)==3 and sys.argv[1]=='--exercise':
    print(json.dumps(exercise(Path(sys.argv[2]))));raise SystemExit(0)
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('test-'+str(time.time_ns()));OUT.mkdir()
r={'passed':False,'nativeAcceptance':False,'scope':'Actual procfs self ELF/libc plus synthetic hostile maps; no native compositor/plugin load','mutants':[]}
try:
    for p in [ROOT/'guard.py',Path(__file__)]:shutil.copy2(p,OUT/p.name)
    r['inputs']={str(p):sha(p) for p in [ROOT/'guard.py',Path(__file__)]};r['checks']=exercise(OUT/'guard.py')
    source=(OUT/'guard.py').read_text()
    for name,old,new in [('digest-bypass','actual==expected','True'),('start-bypass',"process_identity((proc/'stat').read_text(),pid=pid)==start",'True'),('inode-bypass','mapped[p]==identities[p]','True'),('alias-bypass',"not any(Path(q.removesuffix(' (deleted)')).name==Path(p).name and q!=p for q in mapped)",'True')]:
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
