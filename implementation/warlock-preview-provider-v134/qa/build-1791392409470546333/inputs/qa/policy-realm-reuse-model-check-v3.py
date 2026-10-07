"""Execute each named realm reuse scenario explicitly, preserving model scope."""
import hashlib,json,pathlib,re,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path(__file__).resolve().parents[1]
out=r/'qa'/('policy-realm-reuse-model-v3-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tool=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint')
names=['spec/policy_realm_reuse_v3.qnt','spec/policy_realm_reuse_tests_v3.qnt','qa/policy-realm-reuse-model-check-v3.py']
d={'passed':False,'inputs':{n:sha(r/n) for n in names},'quint':{'path':str(tool),'sha256':sha(tool)},'commands':[],'scope':'Native driver realm custody abstraction only; original independent physical, terminal, journal and native permanent-retirement facts remain external authorities. Named selection and invariant samples are model evidence, not actual GTK/WebKit, physical reveal or release acceptance.','nativeAcceptance':False,'fullReleaseAccepted':False}
def run(name,args):
 p=subprocess.run(args,cwd=out/'inputs/spec',capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 d['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 assert p.returncode==0,p.stderr or p.stdout
try:
 for n in names:
  target=out/'inputs'/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(r/n,target)
 selected=re.findall(r'run (\w+)\s*=',(r/names[1]).read_text());assert len(selected)==8
 run('typecheck',[str(tool),'typecheck','policy_realm_reuse_tests_v3.qnt'])
 run('selected',[str(tool),'test','policy_realm_reuse_tests_v3.qnt','--main=policy_realm_reuse_tests_v3','--backend=typescript','--match=^('+'|'.join(selected)+')$','--seed=1300040','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')])
 assert len(list(out.glob('named-*.itf.json')))==8
 run('samples',[str(tool),'run','policy_realm_reuse_v3.qnt','--main=policy_realm_reuse_v3','--backend=typescript','--invariant=safety','--seed=1300041','--max-samples=200','--max-steps=32','--out-itf='+str(out/'samples.itf.json')])
 assert all(sha(r/n)==h for n,h in d['inputs'].items()) and sha(tool)==d['quint']['sha256']
 d.update(passed=True,namedScenarios=8,invariantSamples=200)
except Exception as error:d['error']=repr(error)
d['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps({'passed':d['passed'],'report':str(out/'report.json'),'error':str(d.get('error',''))[:2200]}),flush=True)
raise SystemExit(not d['passed'])


