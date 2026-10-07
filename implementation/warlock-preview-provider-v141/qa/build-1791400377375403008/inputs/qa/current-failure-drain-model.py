"""Execute each named realm reuse scenario explicitly, preserving model scope."""
import hashlib,json,pathlib,re,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path(__file__).resolve().parents[1]
out=r/'qa'/('current-failure-drain-model-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tool=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint')
names=['spec/current_failure_drain.qnt','spec/current_failure_drain_tests.qnt','qa/current-failure-drain-model.py']
d={'passed':False,'inputs':{n:sha(r/n) for n in names},'quint':{'path':str(tool),'sha256':sha(tool)},'commands':[],'scope':'Current failure drain abstraction only: failure/owned custody/quarantine, independent native settlement, strict close before failure exit, later intent no cancellation/reset, stale error no authority and explicit Unknown. NativeSettled represents separately required original physical/journal/confirmation witnesses, never a UI inferred result. This model does not prove actual native source/receipts/liveness/deadlines, graceful recovery, physical reveal or release; actual Native168 failure and fresh native fix oracle qualify separately.','nativeAcceptance':False,'fullReleaseAccepted':False}
def run(name,args):
 p=subprocess.run(args,cwd=out/'inputs/spec',capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 d['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 assert p.returncode==0,p.stderr or p.stdout
try:
 for n in names:
  target=out/'inputs'/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(r/n,target)
 selected=re.findall(r'run (\w+)\s*=',(r/names[1]).read_text());assert len(selected)==8
 run('typecheck',[str(tool),'typecheck','current_failure_drain_tests.qnt'])
 run('selected',[str(tool),'test','current_failure_drain_tests.qnt','--main=current_failure_drain_tests','--backend=typescript','--match=^('+'|'.join(selected)+')$','--seed=1390041','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')])
 assert len(list(out.glob('named-*.itf.json')))==8
 run('samples',[str(tool),'run','current_failure_drain.qnt','--main=current_failure_drain','--backend=typescript','--invariant=safety','--seed=1390042','--max-samples=200','--max-steps=32','--out-itf='+str(out/'samples.itf.json')])
 assert all(sha(r/n)==h for n,h in d['inputs'].items()) and sha(tool)==d['quint']['sha256']
 d.update(passed=True,namedScenarios=8,invariantSamples=200)
except Exception as error:d['error']=repr(error)
d['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps({'passed':d['passed'],'report':str(out/'report.json'),'error':str(d.get('error',''))[:2200]}),flush=True)
raise SystemExit(not d['passed'])



