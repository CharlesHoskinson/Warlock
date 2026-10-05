"""Independent final330 replay; preserves all unsafe predecessor controls."""
import copy,hashlib,importlib.util,json,mmap,os,resource,shutil,subprocess,sys,time
from pathlib import Path
if len(sys.argv)==5 and sys.argv[1]=='--fifo-child':
 spec=importlib.util.spec_from_file_location('guard',sys.argv[2]);g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
 try:g.pinned(sys.argv[3],sys.argv[4],time.monotonic()+0.15)
 except g.Refused as e:print(json.dumps({'refused':True,'reason':str(e)}));raise SystemExit(0)
 raise SystemExit('unsafe FIFO acceptance')
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent/'elm-own-popup-runtime-closure-guard-v330';OUT=ROOT/('review-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
r={'passed':False,'nativeAcceptance':False,'authenticatedHost':False,'scope':'Final330 exact source/closure; actual self procfs/owned file interleavings/mmap/FIFO CPU checks, no native compositor/host/menu proof','entries':[],'checks':[]}
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def pin(p,w=None):
 p=Path(p);d=sha(p);assert w is None or w==d,str(p);r['entries'].append({'path':str(p),'sha256':d,'size':p.stat().st_size})
def module():
 spec=importlib.util.spec_from_file_location('guard',OUT/'guard.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);return g
try:
 p=SOURCE/'component-manifest.json';pin(p,'66527cb94aa2fc22e7b2bfc29af1e868a90a42668a2008af33adcc204583960f');manifest=json.loads(p.read_text());assert manifest['sourceHeld'] and manifest['evidenceIntegrityPassed']
 for rel,row in manifest['files'].items():pin(SOURCE/rel,row['sha256'])
 for path,row in manifest.get('externalFiles',{}).items():
  if 'symlink' in row:
   assert Path(path).is_symlink() and os.readlink(path)==row['symlink'];r['entries'].append({'path':path,'symlink':row['symlink']})
  else:pin(path,row['sha256'])
 for p in [SOURCE/'guard.py',SOURCE/'qa/test.py']:shutil.copy2(p,OUT/p.name);(OUT/p.name).chmod(0o444)
 for kind in ['control','descriptor-replaced','closure-replaced']:
  g=module();runtime=OUT/kind;runtime.mkdir();g.TUPLE=runtime;paths={}
  for name in ['core','plugin','observer','libaquamarine.so.fixture','alternate-core','libaquamarine.so.alternate']:
   p=runtime/name;p.write_bytes(name.encode());paths[name]=p
  closure=runtime/'closure.json';c={'passed':True,'missingSymbols':{},'currentLinkerCache':{'sha256':sha('/etc/ld.so.cache')},'tools':{},'libraries':{str(paths['libaquamarine.so.fixture']):sha(paths['libaquamarine.so.fixture'])}};closure.write_text(json.dumps(c))
  descriptor=runtime/'native-build-report.json';d={'linkClosureReport':str(closure),'linkClosureReportSHA256':sha(closure),'binary':str(paths['core']),'sha256':sha(paths['core']),'plugin':{'path':str(paths['plugin']),'sha256':sha(paths['plugin'])},'observer':{'path':str(paths['observer']),'sha256':sha(paths['observer'])}};descriptor.write_text(json.dumps(d));g.DESCRIPTOR_SHA=sha(descriptor)
  original=g.read_pinned;events=[]
  def interleaved(path,expected,deadline,**kw):
   raw=original(path,expected,deadline,**kw)
   if kind=='descriptor-replaced' and Path(path)==descriptor:
    changed=dict(d);changed.update(binary=str(paths['alternate-core']),sha256=sha(paths['alternate-core']));stage=runtime/'next.json';stage.write_text(json.dumps(changed));os.replace(stage,descriptor);events.append('descriptor changed after checked bytes retained')
   if kind=='closure-replaced' and Path(path)==closure:
    changed=dict(c);changed['libraries']={str(paths['libaquamarine.so.alternate']):sha(paths['libaquamarine.so.alternate'])};stage=runtime/'next.json';stage.write_text(json.dumps(changed));os.replace(stage,closure);events.append('closure changed after checked bytes retained')
   return raw
  g.read_pinned=interleaved;result=g.verify_tuple(deadline=time.monotonic()+5.0)
  assert str(paths['core']) in result['artifacts'] and str(paths['alternate-core']) not in result['artifacts'];assert result['libraries']==c['libraries'];assert not result['authenticatedHost'] and not result['nativeAcceptance']
  r['checks'].append({'name':kind,'result':'original checked bytes only','interleavings':events,'scope':'synthetic tuple data in actual function'})
 g=module();maps=g.parse_maps(Path('/proc/self/maps').read_text());binary=str(Path('/proc/self/exe').resolve());lib=next(p for p in maps if Path(p).name.startswith('libc.so'));alternate=OUT/Path(lib).name;shutil.copy2(lib,alternate)
 evidence={'artifacts':{binary:sha(binary)},'libraries':{lib:sha(lib)}};start=g.process_identity(Path('/proc/self/stat').read_text(),pid=os.getpid())
 result=g.verify_process(pid=os.getpid(),start=start,tuple_evidence=evidence,deadline=time.monotonic()+5.0);assert not result['authenticatedHost'] and not result['nativeAcceptance'];r['checks'].append({'name':'actual self binary/libc bracket','result':result})
 def reject(name,f):
  try:f()
  except g.Refused as e:r['checks'].append({'name':name,'refused':str(e)});return
  raise AssertionError('unsafe acceptance: '+name)
 with alternate.open('rb') as f:
  view=mmap.mmap(f.fileno(),4096,access=mmap.ACCESS_READ)
  try:reject('actual alternate libc data map',lambda:g.verify_process(pid=os.getpid(),start=start,tuple_evidence=evidence,deadline=time.monotonic()+5.0))
  finally:view.close()
 raw=Path('/proc/self/stat').read_text();tail=raw[raw.rfind(')')+2:].split();bad_start=tail.copy();bad_start[19]='1'*5000;bad_state=tail.copy();bad_state[0]='?';st=Path('/').stat();identity=(os.major(st.st_dev),os.minor(st.st_dev),st.st_ino)
 cases=[('5000-digit map inode',lambda:g.parse_maps('100-200 r-xp 0 00:01 '+'1'*5000+' /tmp/a')),('5000-digit process start',lambda:g.process_identity(str(os.getpid())+' (owned) '+' '.join(bad_start),pid=os.getpid())),('5000-digit mount device',lambda:g.map_identity('/bin',identity,'1 0 '+'1'*5000+':1 / / rw - btrfs /dev/fake rw')),('unknown process state',lambda:g.process_identity(str(os.getpid())+' (owned) '+' '.join(bad_state),pid=os.getpid())),('reversed map range',lambda:g.parse_maps('200-100 r-xp 0 00:01 1 /tmp/a'))]
 for name,f in cases:reject(name,f)
 # Invalid public PID/start inputs must fail before ANY stat/read.
 from unittest.mock import patch
 for pid,started in [(True,1),('not-a-pid',1),(-1,1),(2,True),(2,2**64)]:
  with patch.object(g.Path,'stat',side_effect=AssertionError('IO before caller guard')),patch.object(g,'read_text_bounded',side_effect=AssertionError('IO before caller guard')):
   reject('early PID/start '+repr((pid,started)),lambda pid=pid,started=started:g.verify_process(pid=pid,start=started,tuple_evidence={},deadline=time.monotonic()+1.0))
 fifo=OUT/'owned-fifo';os.mkfifo(fifo,0o600);stdout=OUT/'fifo.stdout';stderr=OUT/'fifo.stderr'
 with stdout.open('wb') as o,stderr.open('wb') as e:
  command=[sys.executable,'-B',str(Path(__file__)),'--fifo-child',str(OUT/'guard.py'),str(fifo),'0'*64];child=subprocess.Popen(command,stdout=o,stderr=e);began=time.monotonic();proc=Path('/proc')/str(child.pid);started=proc.joinpath('stat').read_text().split(')')[-1].split()[19];code=child.wait(timeout=0.8)
 parsed=json.loads(stdout.read_bytes());assert code==0 and parsed['refused'] is True and 'regular' in parsed['reason'];fifo.unlink();r['checks'].append({'name':'actual FIFO rejects before original150ms deadline','pid':child.pid,'start':started,'exitCode':code,'elapsedIncludingStartup':time.monotonic()-began,'result':parsed})
 for target in [OUT,OUT/'symlink']:
  if target.name=='symlink':target.symlink_to(OUT/'guard.py')
  reject('nonregular/nofollow '+target.name,lambda target=target:g.pinned(target,'0'*64,time.monotonic()+0.15))
 q=subprocess.run([sys.executable,'-B',str(OUT/'test.py'),'--exercise',str(OUT/'guard.py')],capture_output=True,timeout=30);(OUT/'suite.stdout').write_bytes(q.stdout);(OUT/'suite.stderr').write_bytes(q.stderr);assert q.returncode==0,q.stderr.decode(errors='replace');suite=json.loads(q.stdout);assert len(suite)==42;r['currentSuiteChecks']=suite
 source_report=Path(manifest['testReport']);pin(source_report);d=json.loads(source_report.read_text());assert d['passed'] and len(d['checks'])==42 and len(d['mutants'])==5 and all(x['killed'] for x in d['mutants']);r['sourceTestReport']=str(source_report)
 r['real171Tuple']=module().verify_tuple(deadline=time.monotonic()+60.0);assert len(r['real171Tuple']['libraries'])==171
 r['tools']={str(Path(sys.executable).resolve()):sha(Path(sys.executable).resolve())};r['passed']=True
except Exception as e:r['error']=repr(e)
finally:(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');print('PASS '+str(len(r['entries']))+' entries' if r['passed'] else r.get('error'))
if not r['passed']:raise SystemExit(1)
