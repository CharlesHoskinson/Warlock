"""Compare selected Quint lifecycle traces with the actual controlled C API."""
import hashlib,json,pathlib,re,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('live-window-detachment-model-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tool='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
names=[str(p.relative_to(root)) for p in (root/'native').glob('*') if p.is_file()]+['spec/live_window_detachment.qnt','spec/live_window_detachment_tests.qnt',str(pathlib.Path(__file__).relative_to(root))]
report={'passed':False,'inputs':{rel:sha(root/rel) for rel in names},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual controlled C factory, authenticated synthetic Native socket, Endpoint/Broker actor/job counts, terminal proof retention, original actor processing journal, independent confirmation and strict owning Bootstrap close. Actual Bootstrap attached state compared after every event, including no borrowed Endpoint after strict close and exact-channel reattachment. Different actual Native Bootstrap refuses before owner mutation. Compare native active claim, receiver epoch, job/actor/proof counts, terminal state, C empty predicate and actual operation outcome after every selected/sampled event. Through/phase/requested are history ghosts excluded from actual comparison; failed construction consumption is witnessed by next actual grant. Stable Native binding checked at each event. Distinct native scoped readiness/completion/final processing leaves synthetic Native incarnation Active on every event; early readiness stays pending until original job proof/final ACK barriers. Wrong permanent acknowledgment and sender epochs refuse. No actual capture pixels/Wayland window/Core/WebKit/native GUI acceptance. Counter exhaustion separately witnessed by actual uint64 C derivative.'}
def run(name,args,stdin=None,cwd=None,required=True):
 p=subprocess.run(args,input=stdin,cwd=cwd or out/'inputs',capture_output=True,text=True,timeout=180)
 (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
 report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if required:assert p.returncode==0,p.stderr or p.stdout
 return p
def decode(v):
 if isinstance(v,list):return [decode(x) for x in v]
 if isinstance(v,dict):return int(v['#bigint']) if '#bigint' in v else {k:decode(x) for k,x in v.items()}
 return v
try:
 for rel in names:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']).stdout)
 args=['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/live-window-detachment-replay.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','-o',str(out/'checks'),*flags]
 run('compile',args)
 folder=out/'inputs/spec';selected=re.findall(r'run (\w+)\s*=',(folder/'live_window_detachment_tests.qnt').read_text());assert len(selected)==21
 run('typecheck',[tool,'typecheck','live_window_detachment_tests.qnt'],cwd=folder)
 run('selected',[tool,'test','live_window_detachment_tests.qnt','--main=live_window_detachment_tests','--backend=typescript','--match=^('+'|'.join(selected)+')$','--seed=1070011','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')],cwd=folder)
 assert len(list(out.glob('named-*.itf.json')))==21
 run('samples',[tool,'run','live_window_detachment.qnt','--main=live_window_detachment','--backend=typescript','--invariant=safety','--seed=1070012','--max-samples=250','--max-steps=50','--n-traces=12','--out-itf='+str(out/'sample-{seq}.itf.json')],cwd=folder)
 traces=[];witnesses={}
 for path in sorted(out.glob('*.itf.json')):
  states=[v['s'] for v in decode(json.loads(path.read_text()))['states']];wanted=[];count=0
  for state in states:
   if len(state['history'])==count:continue
   count=len(state['history']);wanted.append({k:(str(v) if k=='epoch' else v) for k,v in state.items() if k not in ('history','phase','through','requested')})
  stdin='\n'.join(states[-1]['history'])+'\n'
  actual=[json.loads(v) for v in run('replay-'+path.stem,[str(out/'checks')],stdin).stdout.splitlines()]
  assert actual==wanted,(path.name,actual,wanted)
  traces.append({'trace':path.name,'statesCompared':len(actual),'normalOwnedExit':True});witnesses[path.name]=(stdin,wanted)
 mutants=[]
 for name,header,old,new,witness in [
  ('keep-borrowed-receipt-after-endpoint-destruction','native/imported-clients.cpp','if(bootstrap)bootstrapReleaseImported(bootstrap);',';','settledCloseReleasesClaim'),
  ('reset-receiver-epoch','native/imported-clients.cpp','registerControlView(popup,binding,controlClaim->epoch())','registerControlView(popup,binding)','replacementEpochPersists'),
  ('release-claim-on-refused-close','native/imported-clients.cpp','try {require(warlock_imported_clients_empty(owner),','try {if(owner->controlled)owner->controlClaim->complete();require(warlock_imported_clients_empty(owner),','activeCloseRefuses')]:
  target=out/name;shutil.copytree(out/'inputs',target);p=target/header;s=p.read_text();assert s.count(old)==1;p.write_text(s.replace(old,new))
  mutant=[*args];mutant[mutant.index('-o')+1]=str(target/'checks');run(name+'-compile',mutant,cwd=target)
  path=next(v for v in witnesses if witness in v);stdin,wanted=witnesses[path]
  result=run(name+'-replay',[str(target/'checks')],stdin,required=False)
  actual=[json.loads(v) for v in result.stdout.splitlines()];assert actual!=wanted,(name,result.stderr)
  # Crashes are not behavior witnesses. Each derivative must report its own
  # compared state or fail a specific original ownership/teardown assertion.
  if result.returncode:assert result.returncode==1 and any(line.startswith('Realm replay ') for line in result.stderr.splitlines()),(name,result.stderr)
  mutants.append({'name':name,'compiled':True,'witness':path,'differentObservableState':True,'exitCode':result.returncode})
 assert all(sha(root/rel)==value for rel,value in report['inputs'].items())
 report.update(passed=True,selectedNames=selected,namedScenarios=21,invariantSamples=250,coupledTraces=traces,statesCompared=sum(v['statesCompared'] for v in traces),unsafeCompiledVariantsDetected=3,mutants=mutants)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1800]}),flush=True);sys.exit(not report['passed'])
