"""Freeze exact compiled Escape source and controls; native acceptance separate."""
import hashlib,json,os,resource,stat,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
builds=list((ROOT/'qa').glob('build-*/report.json'));assert len(builds)==1
p=builds[0];r=json.loads(p.read_text());assert r['passed']
for rel,digest in r['inputs'].items():assert sha(ROOT/rel)==digest and sha(p.parent/'inputs'/rel)==digest
assert sha(p.parent/'elm-host')==r['binarySHA256']
for field in ['compilerDependencies','tools','linkedLibraries']:
 for path,row in r[field].items():assert sha(path)==row['sha256']
for rel,digest in r['artifacts'].items():assert sha(p.parent/rel)==digest
controls=list((ROOT/'qa').glob('mutations-*/report.json'));assert len(controls)==1
c=controls[0];m=json.loads(c.read_text());assert m['passed'] and len(m['controls'])==11 and all(v['accepted'] for v in m['controls'])
for row in m['controls']:assert sha(c.parent/row['name']/'checks')==row['binarySHA256']
assert m['sourceSHA256']==sha(ROOT/'native/shared-context.h')
ancestor=REPO/'implementation/elm-shared-held-key-host-v171';changes=[]
for name in ['src','native','adapter','assets']:
 for q in (ancestor/name).iterdir():
  if q.is_file() and q.read_bytes()!=(ROOT/name/q.name).read_bytes():changes.append(str(q.relative_to(ancestor)))
assert set(changes)=={'native/shared-context.h','native/shared-context-test.c'},changes
model=REPO/'implementation/elm-native-escape-order-model-v183/component-manifest.json'
v=json.loads(model.read_text());assert v['passed'] and len(v['files'])==68
for row in v['files']:assert sha(model.parent/row['path'])==row['sha256']
files=[]
for q in sorted(ROOT.rglob('*')):
 if q==ROOT/'component-manifest.json':continue
 st=q.lstat();row={'path':str(q.relative_to(ROOT)),'mode':stat.S_IMODE(st.st_mode)}
 if q.is_symlink():row['symlink']=os.readlink(q)
 elif stat.S_ISREG(st.st_mode):row.update(sha256=sha(q),size=st.st_size)
 elif q.is_dir():continue
 else:raise RuntimeError('Unexpected special file '+str(q))
 files.append(row)
assert len(files)>300 and {str(v.relative_to(ROOT)) for v in [p,c,*[ROOT/x for x in r['inputs']]]}<={row['path'] for row in files}
result={'schema':1,'passed':True,'nativeAcceptance':False,'releaseAcceptance':False,'buildReport':str(p),'buildReportSHA256':sha(p),'mutationReport':str(c),'mutationReportSHA256':sha(c),'modelManifest':str(model),'modelManifestSHA256':sha(model),'files':files,'scope':'Actual optimized Elm host,168 actual C helper checks,10 compiled rejected mutations and prior183 model; native input, GPU, hardware, ATIME and full release remain separate'}
with (ROOT/'component-manifest.json').open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':True,'manifest':str(ROOT/'component-manifest.json'),'sha256':sha(ROOT/'component-manifest.json'),'files':len(files)}))
