"""Explicitly selected cache traces for replay against real native pixels."""
import hashlib,json,pathlib,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'qa'/('model-'+str(time.time_ns()));OUT.mkdir()
TOOL='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
paths=[pathlib.Path(__file__),ROOT/'spec/cache.qnt',ROOT/'SPEC.md']
inputs={str(p):sha(p) for p in paths}
for p in paths:shutil.copy2(p,OUT/p.name)
r={'passed':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'qaScope':scope,'inputs':inputs,'commands':[],
   'scope':'Five fixed SHM cache scenarios; exported projections require separate actual native replay. No fence/layout/presentation or full release claim.'}
try:
 names=['defaultSyncTest','mergeEmptyTest','inheritedDesyncTest','queuedNullTest','destroyCacheTest']
 for name,args in [('typecheck',[TOOL,'typecheck',str(OUT/'cache.qnt')]),('selected',[TOOL,'test',str(OUT/'cache.qnt'),'--main=cache','--backend=typescript','--match=^('+'|'.join(names)+')$','--seed=730011','--max-samples=1','--out-itf='+str(OUT/'named-{test}-{seq}.itf.json')])]:
  p=subprocess.run(args,capture_output=True,text=True,timeout=180);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);r['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});assert p.returncode==0,p.stdout+p.stderr
 traces=sorted(OUT.glob('named-*.itf.json'));assert len(traces)==5
 r.update(passed=True,selectedNames=names,traces={str(p):sha(p) for p in traces},states=sum(len(json.loads(p.read_text())['states']) for p in traces))
 assert all(sha(p)==h for p,h in inputs.items())
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
report=OUT/'report.json';report.write_text(json.dumps(r,indent=2)+'\n')
if r['passed']:(ROOT/'qa/model-report.json').write_text(json.dumps({'path':str(report),'sha256':sha(report)},indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'report':str(report),'error':r.get('error')}),flush=True)
raise SystemExit(not r['passed'])
