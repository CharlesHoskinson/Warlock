"""Retain native peer diagnostics using the exact failed-v3 compiled fixture."""
import hashlib,json,pathlib,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path(__file__).resolve().parents[1]
base=r/'qa/policy-driver-realm-reuse-check-v3-1791388582531783144'
out=r/'qa'/('policy-driver-realm-reuse-diagnostic-v4-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=json.loads((base/'report.json').read_text());assert not prior['passed']
assert any(c['name']=='compile-owner' and c['exitCode']==0 for c in prior['commands'])
for n,h in prior['inputs'].items():assert sha(r/n)==h,n
for n,h in prior['artifacts'].items():assert sha(base/n)==h,n
js=r/'qa/policy-driver-realm-reuse-roundtrip-v2.js';shutil.copy2(js,out/'roundtrip.js')
args=['node',str(out/'roundtrip.js'),str(base/'driver'),str(base/'policy.js'),str(base/'inputs/assets/native-preview-control-outbox.js')]
p=subprocess.run(args,cwd=out,capture_output=True,text=True,timeout=180)
(out/'roundtrip.stdout').write_text(p.stdout);(out/'roundtrip.stderr').write_text(p.stderr)
d={'passed':p.returncode==0,'priorReport':{'path':str(base/'report.json'),'sha256':sha(base/'report.json')},'inputs':{str(js):sha(js)},'command':args,'exitCode':p.returncode,'nativeAcceptance':False,'fullReleaseAccepted':False}
if d['passed']:d['evidence']=json.loads(p.stdout)
d['artifacts']={str(x.relative_to(out)):sha(x) for x in out.rglob('*') if x.is_file()}
(out/'report.json').write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps({'passed':d['passed'],'report':str(out/'report.json'),'stderr':p.stderr[:3000]}),flush=True)
raise SystemExit(not d['passed'])
