import hashlib,json,os,resource,stat
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
reports=list(ROOT.glob('build-*/report.json')) if (ROOT/'build.py').is_file() else list((ROOT/'qa').glob('build-*/report.json'))
assert len(reports)==1
p=reports[0];r=json.loads(p.read_text());assert r['passed']
for rel,digest in r['inputs'].items():assert sha(ROOT/rel)==digest and sha(p.parent/'inputs'/rel)==digest
if (ROOT/'build.py').is_file():
 for name in ['module','client']:assert sha(r[name])==r[name+'SHA256']
 for field in ['owningFiles','dependencies']:
  for path,digest in r[field].items():assert sha(path)==digest
else:
 assert sha(p.parent/'elm-host')==r['binarySHA256']
 for field in ['compilerDependencies','tools','linkedLibraries']:
  for path,row in r[field].items():assert sha(path)==row['sha256']
 for rel,digest in r['artifacts'].items():assert sha(p.parent/rel)==digest
 old=ROOT.parents[1]/'implementation/elm-shared-geometry-carrier-v422';changes=[]
 for name in ['src','native','adapter','assets']:
  for q in (old/name).iterdir():
   if q.is_file() and q.read_bytes()!=(ROOT/name/q.name).read_bytes():changes.append(str(q.relative_to(old)))
 assert changes==['native/shared-context.h'],changes
files=[]
for q in sorted(ROOT.rglob('*')):
 if q==ROOT/'component-manifest.json':continue
 st=q.lstat();row={'path':str(q.relative_to(ROOT)),'mode':stat.S_IMODE(st.st_mode)}
 if q.is_symlink():row['symlink']=os.readlink(q)
 elif stat.S_ISREG(st.st_mode):row.update(sha256=sha(q),size=st.st_size)
 elif q.is_dir():continue
 else:raise RuntimeError('Runtime special file '+str(q))
 files.append(row)
assert len(files)>=30, 'Empty/incomplete component inventory'
assert {str(v.relative_to(ROOT)) for v in [p,*[ROOT/x for x in r['inputs']]]} <= {v['path'] for v in files}
result={'schema':1,'passed':True,'nativeAcceptance':False,'releaseAcceptance':False,'buildReport':str(p),'buildReportSHA256':sha(p),'files':files,'scope':'Compiled private protocol8 fixture' if (ROOT/'build.py').is_file() else 'Actual compiled shared Elm168 with QA-only GTK key telemetry; existing owning context/host/surface tests, no native acceptance yet'}
with (ROOT/'component-manifest.json').open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':True,'manifest':str(ROOT/'component-manifest.json'),'sha256':sha(ROOT/'component-manifest.json'),'files':len(files)}))
