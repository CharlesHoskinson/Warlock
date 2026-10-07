"""Compare explicitly selected Quint job-control traces with actual native issuer."""
import hashlib,json,pathlib,re,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('capture-intent-model-check-v3-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tool='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
names=[str(p.relative_to(root)) for p in (root/'native').glob('*') if p.is_file()]+['spec/capture_intent.qnt','spec/capture_intent_tests.qnt',str(pathlib.Path(__file__).relative_to(root))]
report={'passed':False,'inputs':{rel:sha(root/rel) for rel in names},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual native capture intent and controlled ticket prefix compared with14 explicitly selected Quint scenarios and sampled traces in three authenticated synthetic socket failure modes: capture refusal, malformed completion and unavailable FD transport. Original exact wire/context/deadline persist; no Unknown replay or false charge/proof/binding closure. Three unsafe native variants must compile and differ on original trace states. No actual capture pixels/FD/backend reconciliation/WebKit/native GUI or full release acceptance.'}
def run(name,args,stdin=None,cwd=None):
 p=subprocess.run(args,input=stdin,cwd=cwd or out/'inputs',capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 assert p.returncode==0,p.stderr or p.stdout
 return p.stdout
def decode(v):
 if isinstance(v,list):return [decode(x) for x in v]
 if isinstance(v,dict):return int(v['#bigint']) if '#bigint' in v else {k:decode(x) for k,x in v.items()}
 return v
try:
 for rel in names:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']))
 args=['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/capture-intent-replay-v2.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','-o',str(out/'checks'),*flags]
 run('compile',args)
 folder=out/'inputs/spec';selected=re.findall(r'run (\w+)\s*=',(folder/'capture_intent_tests.qnt').read_text());assert len(selected)==14
 run('typecheck',[tool,'typecheck','capture_intent_tests.qnt'],cwd=folder)
 run('selected',[tool,'test','capture_intent_tests.qnt','--main=capture_intent_tests','--backend=typescript','--match=^('+'|'.join(selected)+')$','--seed=1040031','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')],cwd=folder)
 assert len(list(out.glob('named-*.itf.json')))==14
 run('samples',[tool,'run','capture_intent.qnt','--main=capture_intent','--backend=typescript','--invariant=safety','--seed=1040032','--max-samples=100','--max-steps=30','--n-traces=8','--out-itf='+str(out/'sample-{seq}.itf.json')],cwd=folder)
 traces=[];witnesses={}
 for path in sorted(out.glob('*.itf.json')):
  states=[v['s'] for v in decode(json.loads(path.read_text()))['states']];wanted=[];count=0
  for state in states:
   if len(state['history'])==count:continue
   count=len(state['history']);wanted.append({k:v for k,v in state.items() if k!='history'})
  stdin='\n'.join(states[-1]['history'])+'\n'
  for mode in ['capture-refused','capture-malformed','capture-fd-missing']:
   actual=[json.loads(v) for v in run('replay-'+mode+'-'+path.stem,[str(out/'checks'),mode],stdin).splitlines()]
   assert actual==wanted,(path.name,mode,actual,wanted)
   traces.append({'trace':path.name,'mode':mode,'statesCompared':len(actual)})
  witnesses[path.name]=(stdin,wanted)

 mutants=[]
 for name,header,old,new,witness in [
  ('forget-original-intent','native/imported_clients.hpp','f.attempted=true;f.capture=captureClient(authority_->native,*f.captureIntent);','f.attempted=true;try{f.capture=captureClient(authority_->native,*f.captureIntent);}catch(...){f.captureIntent.reset();throw;}','originalIntentSurvivesCaptureError'),
  ('repeat-unknown-native-capture','native/imported_clients.hpp','require(!f.attempted && !f.cleanup && !reconciling_,"Single original imported capture");',';','rawRetryCannotCaptureAgain'),
  ('mark-invocation-only-after-reply','native/imported_clients.hpp','f.attempted=true;f.capture=captureClient(authority_->native,*f.captureIntent);','f.capture=captureClient(authority_->native,*f.captureIntent);f.attempted=true;','cancellationAfterUnknownRetainsCharge')]:
  changed=out/name;shutil.copytree(out/'inputs',changed);p=changed/header;s=p.read_text();assert s.count(old)==1;p.write_text(s.replace(old,new))
  mutant=[*args];mutant[mutant.index('-o')+1]=str(changed/'checks');run(name+'-compile',mutant,cwd=changed)
  path=next(v for v in witnesses if witness in v);stdin,wanted=witnesses[path]
  actual=[json.loads(v) for v in run(name+'-replay',[str(changed/'checks'),'capture-refused'],stdin).splitlines()]
  assert actual!=wanted;mutants.append({'name':name,'compiled':True,'witness':path,'differentObservableState':True})
 assert all(sha(root/rel)==value for rel,value in report['inputs'].items())
 report.update(passed=True,selectedNames=selected,namedScenarios=14,invariantSamples=100,coupledTraces=traces,statesCompared=sum(v['statesCompared'] for v in traces),unsafeMutantsDetected=3,mutants=mutants)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:900]}),flush=True);sys.exit(not report['passed'])
