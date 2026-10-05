"""Preserve actual guard file-reopen races and real additional library mapping."""
import hashlib,importlib.util,json,mmap,os,resource,shutil,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent/'elm-own-popup-runtime-closure-guard-v326';OUT=ROOT/('witness-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
for rel in ['guard.py','qa/test.py']:
 p=OUT/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(SOURCE/rel,p);p.chmod(0o444)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module():
 spec=importlib.util.spec_from_file_location('guard',OUT/'inputs/guard.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);return g
r={'passed':False,'nativeAcceptance':False,'scope':'Captured actual guard with owned regular-file atomic replacements and actual self mmap; synthetic tuple data/no compositor/host authentication','inputs':{str(p.relative_to(OUT)):sha(p) for p in (OUT/'inputs').rglob('*') if p.is_file()},'cases':[]}
try:
 for kind in ['control','descriptor-replaced','closure-replaced']:
  g=module();runtime=OUT/kind;runtime.mkdir();g.TUPLE=runtime
  paths={}
  for name in ['core','plugin','observer','libaquamarine.so.fixture','alternate-core','libaquamarine.so.alternate']:
   p=runtime/name;p.write_bytes(name.encode());paths[name]=p
  closure=runtime/'closure.json';c={'passed':True,'missingSymbols':{},'currentLinkerCache':{'sha256':sha('/etc/ld.so.cache')},'tools':{},'libraries':{str(paths['libaquamarine.so.fixture']):sha(paths['libaquamarine.so.fixture'])}};closure.write_text(json.dumps(c))
  descriptor=runtime/'native-build-report.json';d={'linkClosureReport':str(closure),'linkClosureReportSHA256':sha(closure),'binary':str(paths['core']),'sha256':sha(paths['core']),'plugin':{'path':str(paths['plugin']),'sha256':sha(paths['plugin'])},'observer':{'path':str(paths['observer']),'sha256':sha(paths['observer'])}};descriptor.write_text(json.dumps(d));g.DESCRIPTOR_SHA=sha(descriptor)
  original_pinned=g.pinned;events=[]
  def interleaved(path,expected,deadline):
   result=original_pinned(path,expected,deadline)
   if kind=='descriptor-replaced' and Path(path)==descriptor:
    changed=dict(d);changed.update(binary=str(paths['alternate-core']),sha256=sha(paths['alternate-core']));stage=runtime/'next.json';stage.write_text(json.dumps(changed));os.replace(stage,descriptor);events.append('replaced after checked hash before parse')
   if kind=='closure-replaced' and Path(path)==closure:
    changed=dict(c);changed['libraries']={str(paths['libaquamarine.so.alternate']):sha(paths['libaquamarine.so.alternate'])};stage=runtime/'next.json';stage.write_text(json.dumps(changed));os.replace(stage,closure);events.append('replaced after checked hash before parse')
   return result
  g.pinned=interleaved
  result=g.verify_tuple(deadline=time.monotonic()+5.0)
  if kind=='descriptor-replaced':assert str(paths['alternate-core']) in result['artifacts'] and sha(descriptor)!=g.DESCRIPTOR_SHA
  if kind=='closure-replaced':assert str(paths['libaquamarine.so.alternate']) in result['libraries'] and sha(closure)!=d['linkClosureReportSHA256']
  r['cases'].append({'name':kind,'accepted':True,'events':events,'result':result})
 g=module();maps=g.parse_maps(Path('/proc/self/maps').read_text());binary=str(Path('/proc/self/exe').resolve());lib=next(p for p in maps if Path(p).name.startswith('libc.so'));alternate=OUT/Path(lib).name;shutil.copy2(lib,alternate)
 with alternate.open('rb') as f:
  view=mmap.mmap(f.fileno(),4096,access=mmap.ACCESS_READ)
  try:
   raw=Path('/proc/self/maps').read_text();assert str(alternate) in raw
   evidence={'artifacts':{binary:sha(binary)},'libraries':{lib:sha(lib)}};start=g.process_identity(Path('/proc/self/stat').read_text(),pid=os.getpid());result=g.verify_process(pid=os.getpid(),start=start,tuple_evidence=evidence,deadline=time.monotonic()+5.0)
   (OUT/'actual-maps.txt').write_text(raw);r['cases'].append({'name':'additional mapped lookup-library basename','accepted':True,'result':result,'mappedAlternate':str(alternate),'scope':'real data mmap, no claim alternate ELF executed'})
  finally:view.close()
 r['passed']=True
except Exception as e:r['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');print('PASS preserved races/alias' if r['passed'] else r['error'])
if not r['passed']:raise SystemExit(1)
