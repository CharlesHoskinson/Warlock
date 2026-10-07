"""Explicit Quint custody scenarios and compiled guards against actual C/JSC."""
import hashlib,json,pathlib,re,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('policy-driver-refinement-'+str(time.time_ns()));out.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=root/'qa/policy-driver-check-1791374752531149246';prior=json.loads((base/'report.json').read_text());assert prior['passed']
names=list(prior['inputs'])+['spec/native_policy_driver.qnt','spec/native_policy_driver_tests.qnt','qa/policy-driver-refinement.py']
report={'passed':False,'inputs':{n:sha(root/n) for n in names},'commands':[],'priorReport':{'path':str(base/'report.json'),'sha256':sha(base/'report.json')},'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Explicit driver custody abstraction retains staged ticket/issued/dispatch/confirmation order and independent job obligation. Compiled native guard variants run the unchanged actual C/JSC roundtrip oracle. Concrete trace checks use retained original native input, native diagnostics and actual Native/C physical observations. This is not full lifecycle refinement, actual WebKit/window acceptance, output queue resource qualification, process-loss recovery or delayed unissued proposal liveness.'}
def run(name,args,cwd=None,required=True):
 p=subprocess.run(args,cwd=cwd or out/'inputs',capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if required:assert p.returncode==0,p.stderr or p.stdout
 return p
try:
 for rel,value in prior['inputs'].items():assert sha(root/rel)==value,rel
 for rel,value in prior['artifacts'].items():assert sha(base/rel)==value,rel
 for rel in names:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 shutil.copy2(base/'inputs/native/capture-resources.hpp',out/'inputs/native/capture-resources.hpp')
 tool='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint';folder=out/'inputs/spec'
 selected=re.findall(r'run (\w+)\s*=',(folder/'native_policy_driver_tests.qnt').read_text());assert len(selected)==14
 run('typecheck',[tool,'typecheck','native_policy_driver_tests.qnt'],folder)
 run('selected',[tool,'test','native_policy_driver_tests.qnt','--main=native_policy_driver_tests','--backend=typescript','--match=^('+'|'.join(selected)+')$','--seed=1200001','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')],folder)
 assert len(list(out.glob('named-*.itf.json')))==14
 run('samples',[tool,'run','native_policy_driver.qnt','--main=native_policy_driver','--backend=typescript','--invariant=safety','--seed=1200002','--max-samples=200','--max-steps=32','--out-itf='+str(out/'samples.itf.json')],folder)
 # Link abstract stages to the concrete retained native trace, without claiming
 # that a custody-only model predicts the original independent Elm lifecycle.
 trace=json.loads((base/'steps.json').read_text());states=[r['result']['result'] for r in trace if r['input']['op']=='inspect' and r['result'].get('ok')];assert len(states)>=20
 witnesses={}
 for index,s in enumerate(states):
  p=s['privatePolicy'];t=s['transport'];known=sum(len(r['model']['known']) for r in p['models'])
  if s['ticketUnnotified'] and s['postedTickets']==1 and p['realm']['ingress']['pending']==1 and t['deliveredThrough']=='0':witnesses.setdefault('retained-before-notify',index)
  if not s['ticketUnnotified'] and s['postedTickets']==1 and p['realm']['ingress']['pending']==0 and t['deliveredThrough']=='0' and known==1:witnesses.setdefault('notified-before-dispatch',index)
  if s['confirmations']==1 and t['deliveredThrough']=='1' and known==1:witnesses.setdefault('returned-before-confirm',index)
  if s['confirmations']==0 and t['deliveredThrough']=='1' and known==1:witnesses.setdefault('confirmation-not-settlement',index)
  if s['retainedInputs']==1065 and known==1 and any(not r['model']['demand'] for r in p['models']):witnesses.setdefault('quarantine-with-full-queue',index)
  if s['retainedInputs']==1 and s['retainedInputBytes']>9*1024*1024:witnesses.setdefault('aggregate-byte-custody',index)
  assert 0<=s['retainedInputs']<=1065 and 0<=s['retainedInputBytes']<=16*1024*1024
  assert int(t['deliveredThrough'])<=int(t['nativeIssuedThrough'])
 assert set(witnesses)=={'retained-before-notify','notified-before-dispatch','returned-before-confirm','confirmation-not-settlement','quarantine-with-full-queue','aggregate-byte-custody'}
 order=[witnesses[k] for k in ['retained-before-notify','notified-before-dispatch','returned-before-confirm','confirmation-not-settlement','quarantine-with-full-queue','aggregate-byte-custody']];assert order==sorted(set(order))
 report['concreteTraceWitnesses']=witnesses;report['concreteObservedStates']=len(states)
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0','javascriptcoregtk-4.1']).stdout)
 original=(out/'inputs/native/preview-policy-driver.cpp').read_text()
 mutants={
 'creator':('if(self->creator!=g_thread_self())return fail(error,"Original driver creator required");','if(false)return fail(error,"Original driver creator required");'),
 'source-epoch':('if(!epoch || epoch!=self->epoch || self->native_closed)return fail(error,"Original native source epoch before input retention");','(void)epoch; if(self->native_closed)return fail(error,"Original native source epoch before input retention");'),
 'queue-items':('if(self->inputs.size()>=input_limit || wire.size()>byte_limit-self->input_bytes)','if(wire.size()>byte_limit-self->input_bytes)'),
 'issued-before-dispatch':('if(!self->pending_issued.empty()) {','if(!self->pending_issued.empty() && self->posts.empty()) {')}
 report['compiledNativeVariants']=[]
 for name,(old,new) in mutants.items():
  assert original.count(old)==1;candidate=out/'inputs/native'/('driver-'+name+'.cpp');candidate.write_text(original.replace(old,new));binary=out/('driver-'+name)
  run('compile-'+name,['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/policy-driver-fixture.cpp',str(candidate),'native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','native/elm-preview-policy.cpp','-o',str(binary),*flags])
  observed=run('guard-'+name,['node',str(out/'inputs/qa/policy-driver-roundtrip.js'),str(binary),str(base/'policy.js'),str(out/'inputs/assets/native-preview-control-outbox.js')],cwd=out,required=False)
  assert observed.returncode!=0 and 'AssertionError' in observed.stderr,(name,observed.stderr)
  # Each failure snapshot belongs to this labeled unsafe derivative.
  failed=out/'failed-steps.json';assert failed.exists();failed.rename(out/('guard-'+name+'-failed-steps.json'))
  report['compiledNativeVariants'].append({'name':name,'sourceSHA256':sha(candidate),'detected':True,'normalCloseClaimed':False})
 report['namedScenarios']=len(selected);report['invariantSamples']=200
 assert all(sha(root/n)==v for n,v in report['inputs'].items());report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:2200]}),flush=True);sys.exit(not report['passed'])
