"""Explicit control-prefix Quint traces coupled to actual native C header."""
import hashlib,json,pathlib,re,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('control-admission-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tool=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint')
names=[str(p.relative_to(root)) for p in (root/'native').glob('*') if p.is_file()]+[str(pathlib.Path(__file__).relative_to(root)),'spec/control_admission.qnt','spec/control_admission_tests.qnt']
report={'passed':False,'inputs':{rel:sha(root/rel) for rel in names},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual native Endpoint receiver enrollment and cleanup-credit guard around original Coordinator/Broker issuance. Explicit selected and sampled Quint traces compare native jobs, intents, scopes, receiver membership/epochs, original deadlines/request floors, reserved credits and pending Unknown issuance. Synthetic authenticated-observation values; real Native metadata/Broker reservations, no capture or compositor. Helpers inactive in provider/WebKit; no renderer tickets, native typed coalescing, physical cleanup, reconciliation or full release acceptance.'}
def run(name,args,stdin=None,cwd=None):
 p=subprocess.run(args,input=stdin,cwd=cwd or out/'inputs',capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 assert p.returncode==0,p.stderr or p.stdout
 return p.stdout
def decode(value):
 if isinstance(value,list):return [decode(v) for v in value]
 if isinstance(value,dict):return int(value['#bigint']) if '#bigint' in value else {k:decode(v) for k,v in value.items()}
 return value
try:
 for rel in names:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']))
 compileArgs=['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/control-admission-replay.cpp','native/preview_uri.cpp','-o',str(out/'checks'),*flags]
 run('compile',compileArgs)
 folder=out/'inputs/spec';selected=re.findall(r'run (\w+)\s*=',(folder/'control_admission_tests.qnt').read_text());assert len(selected)==13
 run('typecheck',[str(tool),'typecheck','control_admission_tests.qnt'],cwd=folder)
 run('selected',[str(tool),'test','control_admission_tests.qnt','--main=control_admission_tests','--backend=typescript','--match=^('+'|'.join(selected)+')$','--seed=980031','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')],cwd=folder)
 assert len(list(out.glob('named-*.itf.json')))==13
 run('samples',[str(tool),'run','control_admission.qnt','--main=control_admission','--backend=typescript','--invariant=safety','--seed=980032','--max-samples=100','--max-steps=20','--n-traces=8','--out-itf='+str(out/'sample-{seq}.itf.json')],cwd=folder)
 traces=[];witnesses={}
 for path in sorted(out.glob('*.itf.json')):
  states=[v['s'] for v in decode(json.loads(path.read_text()))['states']];wanted=[];count=0
  for state in states:
   if len(state['history'])==count:continue
   count=len(state['history']);wanted.append({k:v for k,v in state.items() if k!='history'})
  stdin='\n'.join(states[-1]['history'])+'\n'
  actual=[json.loads(v) for v in run('replay-'+path.stem,[str(out/'checks')],stdin).splitlines()]
  assert actual==wanted,(path.name,actual,wanted)
  traces.append({'trace':path.name,'statesCompared':len(actual)});witnesses[path.name]=(stdin,wanted)
 mutants=[]
 for name,old,new,witness in [
  ('issue-before-cleanup-reservation','if(!prepare(entry))return {ImportedIntentLedger::Admission::Capacity,{},"[]"};\n        auto result=std::invoke(std::forward<F>(issue));','auto result=std::invoke(std::forward<F>(issue));\n        if(!prepare(entry))return {ImportedIntentLedger::Admission::Capacity,{},"[]"};','capacityRefusesBeforeNativeIntent'),
  ('ignore-original-receiver','preview_control_grant_equal(grant_,actual) && importedReceiver(view,owner_,grant_.epoch)','actual.receiver>0 && importedReceiver(view,owner_,grant_.epoch)','foreignReceiverCannotAdmit'),
  ('rollback-unknown-issued-job','auto result=std::invoke(std::forward<F>(issue));','auto result=[&]{try{return std::invoke(std::forward<F>(issue));}catch(...){controls_.release(grant_,jobs_.at(entry).reservation);jobs_.erase(entry);throw;}}();','exceptionKeepsUnknownCleanup'),
  ('forget-retained-cohort-limit','jobs_.size()>=jobLimit_','false','retainedCohortBoundPrecedesNinthJob')]:
  changed=out/name;shutil.copytree(out/'inputs',changed)
  header=changed/'native/imported_control_admission.hpp';s=header.read_text();assert s.count(old)==1;header.write_text(s.replace(old,new))
  mutant_args=[*compileArgs];mutant_args[mutant_args.index('-o')+1]=str(changed/'checks');run(name+'-compile',mutant_args,cwd=changed)
  path=next(v for v in witnesses if witness in v);stdin,wanted=witnesses[path]
  actual=[json.loads(v) for v in run(name+'-replay',[str(changed/'checks')],stdin).splitlines()]
  assert actual!=wanted;mutants.append({'name':name,'witness':path,'differentObservableState':True})
 assert all(sha(root/rel)==value for rel,value in report['inputs'].items())
 report.update(passed=True,selectedNames=selected,namedScenarios=13,invariantSamples=100,coupledTraces=traces,statesCompared=sum(v['statesCompared'] for v in traces),unsafeMutantsDetected=4,mutants=mutants)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:700]}),flush=True);sys.exit(not report['passed'])
