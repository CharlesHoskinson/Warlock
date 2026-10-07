"""Couple the actual two-realm C/JSC custody observations to bounded Quint stages."""
import hashlib,json,pathlib,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path(__file__).resolve().parents[1];out=r/'qa'/('policy-realm-reuse-coupling-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=r/'qa/policy-driver-realm-reuse-check-v5-1791388803876321382'
report=json.loads((base/'report.json').read_text());assert report['passed'] and report['evidence']['originalPolicyPointerPreserved']
for n,h in report['artifacts'].items():assert sha(base/n)==h,n
trace=json.loads((base/'steps.json').read_text())
observations=[(i,row['result']['result']) for i,row in enumerate(trace) if row['input']['op']=='inspect' and row['result']['ok']]
assert len(observations)==11
first=observations[0][1];closed=observations[2][1];opened=observations[6][1];second=observations[9][1];drained=observations[10][1]
assert first['privatePolicy']['realm']['epoch']=='1' and first['privatePolicy']['models'][0]['identity']=='family:21'
assert closed['privatePolicy']['realm']['closed'] and closed['privatePolicy']['models']==[]
assert opened['privatePolicy']['realm']['epoch']=='2' and not opened['privatePolicy']['realm']['closed'] and opened['transport']['nativeIssuedThrough']=='0'
for _,state in observations[3:6]:assert state==closed
assert observations[7][1]==opened
assert observations[8][1]['privatePolicy']['models']==[] and observations[8][1]['transport']['nativeIssuedThrough']=='0'
assert second['privatePolicy']['realm']['epoch']=='2' and second['privatePolicy']['models'][0]['identity']=='family:22'
assert not drained['privatePolicy']['models'] and not drained['retainedInputs'] and not drained['confirmations'] and not drained['returnedEventBatches'] and not drained['transport']['pending']
retired=[row for row in trace if row['input']['op']=='retired-subject'];assert len(retired)==1 and retired[0]['result']['result'][0]['state']=='Retired'
assert trace[-1]['input']['op']=='finish' and trace[-1]['result']['normalOwnedPeerExit'] and trace[-1]['result']['nativeGrantResets']==0
model=r/'spec/policy_realm_reuse_v3.qnt';shutil.copy2(model,out/model.name)
events=['Acquire','Issue','Dispatch','Confirm','Permanent','Terminal','Retire','OldEpoch','ForeignBinding','Reopen','Acquire','Issue','Dispatch','Confirm','Terminal','Retire']
checks={3:'s.epoch==1 and s.duty and not(s.closed)',6:'s.epoch==1 and s.closed and s.permanent',8:'s.epoch==1 and s.closed and s.permanent',9:'s.epoch==2 and not(s.closed) and s.permanent and s.policy==1',13:'s.epoch==2 and s.duty and s.permanent',15:'s.epoch==2 and s.closed and s.permanent and s.policy==1'}
run='init'
for i,event in enumerate(events):
 run+='.then(fire('+event+'))'
 if i in checks:run+='.then(check('+checks[i]+'))'
source='module coupled_realm_reuse {\n import policy_realm_reuse_v3.* from "./policy_realm_reuse_v3"\n action check(ok:bool):bool=all{assert(ok and safety),s\'=s}\n run actualTwoRealmCustody='+run+'\n}\n'
(out/'coupled.qnt').write_text(source)
tool=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint')
args=[str(tool),'test','coupled.qnt','--main=coupled_realm_reuse','--backend=typescript','--match=^actualTwoRealmCustody$','--seed=1300042','--max-samples=1','--out-itf='+str(out/'coupled-{test}-{seq}.itf.json')]
p=subprocess.run(args,cwd=out,capture_output=True,text=True,timeout=180)
(out/'quint.stdout').write_text(p.stdout);(out/'quint.stderr').write_text(p.stderr)
d={'passed':p.returncode==0 and len(list(out.glob('coupled-*.itf.json')))==1,'inputs':{str(model):sha(model),str(base/'report.json'):sha(base/'report.json'),str(base/'steps.json'):sha(base/'steps.json')},'quint':{'path':str(tool),'sha256':sha(tool)},'command':args,'exitCode':p.returncode,'observedStates':len(observations),'coupledQuintChecks':len(checks),'scope':'Actual C/JSC driver custody observations projected to bounded realm lifecycle stages. Explicit effect stages are abstract summaries, not every individual ticket or full lifecycle refinement. Actual C readiness, permanent Retired fact, same policy pointer/binding and strict normal peer close remain independent evidence. Popup quarantine precedes permanent retirement. No GTK/WebKit reopen, direct-retirement, frame/reveal or release qualification.','nativeAcceptance':False,'fullReleaseAccepted':False}
d['artifacts']={str(x.relative_to(out)):sha(x) for x in out.rglob('*') if x.is_file()}
(out/'report.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'passed':d['passed'],'report':str(out/'report.json'),'stderr':p.stderr[:2200]}),flush=True)
raise SystemExit(not d['passed'])
