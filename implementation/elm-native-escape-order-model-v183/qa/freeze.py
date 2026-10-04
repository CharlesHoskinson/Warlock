from pathlib import Path
import hashlib,json,os,resource,stat
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
paths=list((ROOT/'qa').glob('model-*/report.json'));assert len(paths)==1
p=paths[0];r=json.loads(p.read_text());assert r['passed'] and len(r['namedScenarios'])==24 and r['invariantSamples']==1000 and r['maxSteps']==40 and r['mutantsRejected']==6
assert r['sourceSHA256']==sha(ROOT/'spec/recovery.qnt')
for rel,digest in r['artifacts'].items():assert sha(p.parent/rel)==digest
assert len(list(p.parent.glob('named-*.itf.json')))==24
assert sum(v['name'].endswith('-typecheck') and v['exitCode']==0 for v in r['commands'])==6
assert sum(v['name'].endswith('-rejected') and v['exitCode']==1 for v in r['commands'])==6
files=[]
for q in sorted(ROOT.rglob('*')):
 if q==ROOT/'component-manifest.json':continue
 st=q.lstat();row={'path':str(q.relative_to(ROOT)),'mode':stat.S_IMODE(st.st_mode)}
 if q.is_symlink():row['symlink']=os.readlink(q)
 elif stat.S_ISREG(st.st_mode):row.update(sha256=sha(q),size=st.st_size)
 elif q.is_dir():continue
 else:raise RuntimeError('Runtime special file '+str(q))
 files.append(row)
assert len(files)>50
result={'schema':1,'passed':True,'modelAcceptance':True,'nativeAcceptance':False,'releaseAcceptance':False,'scope':'Abstract terminal-order346 extension for native Escape independent of DOM lag. 24 selected scenarios,1000x40 traces,6 typechecked mutations. No C/GTK/native or multiple-view refinement claim.','modelReport':str(p),'modelReportSHA256':sha(p),'files':files}
with (ROOT/'component-manifest.json').open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':True,'manifest':str(ROOT/'component-manifest.json'),'sha256':sha(ROOT/'component-manifest.json'),'files':len(files)}))
