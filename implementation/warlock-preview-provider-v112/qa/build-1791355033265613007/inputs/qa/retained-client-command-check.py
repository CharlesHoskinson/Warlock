"""Explicit control-prefix Quint traces coupled to actual native C header."""
import hashlib,json,pathlib,re,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('retained-client-command-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tool=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint')
names=[str(p.relative_to(root)) for p in (root/'native').glob('*') if p.is_file()]+[str(pathlib.Path(__file__).relative_to(root)),'spec/retained_client_command.qnt','spec/retained_client_command_tests.qnt']
report={'passed':False,'inputs':{rel:sha(root/rel) for rel in names},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual retained native cleanup decoder coupled to explicitly selected and sampled Quint cases, preserving original legacy decoder behavior. Exact Native ready packet permits stale frontend false readiness; no frontend flag grants native readiness, job/token/owned/expiry/coverage authority, or physical/proof completion. Native synthetic packet metadata only; inactive in provider/WebKit. Actual original legacy source/negative controls compile and pass unchanged. No capture, native compositor, actor retirement or full release acceptance.'}
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
 compileArgs=['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/retained-client-command-replay.cpp','native/preview_uri.cpp','-o',str(out/'checks'),*flags]
 run('compile',compileArgs)
 folder=out/'inputs/spec';selected=re.findall(r'run (\w+)\s*=',(folder/'retained_client_command_tests.qnt').read_text());assert len(selected)==14
 run('typecheck',[str(tool),'typecheck','retained_client_command_tests.qnt'],cwd=folder)
 run('selected',[str(tool),'test','retained_client_command_tests.qnt','--main=retained_client_command_tests','--backend=typescript','--match=^('+'|'.join(selected)+')$','--seed=990101','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')],cwd=folder)
 assert len(list(out.glob('named-*.itf.json')))==14
 run('samples',[str(tool),'run','retained_client_command.qnt','--main=retained_client_command','--backend=typescript','--invariant=safety','--seed=990102','--max-samples=100','--max-steps=20','--n-traces=8','--out-itf='+str(out/'sample-{seq}.itf.json')],cwd=folder)
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
 for name,edits,witness in [
  ('require-stale-frontend-readiness', [('if(frontendReady)return decodeClientCommand','if(frontendReady || !frontendReady)return decodeClientCommand')],'lateOriginalOfferCleanup'),
  ('invent-native-readiness', [('const std::optional<Packet>& packet)', 'std::optional<Packet> packet)'), ('require(packet && packet->signaled,"Original native packet readiness before retained cleanup decoding");','require(packet.has_value(),"Original native packet readiness before retained cleanup decoding");packet->signaled=true;')],'frontendTrueCannotGrantNativeReadiness'),
  ('skip-original-job-token-validation', [('return decodeClientCommand(identity,normalized.get(),expected,packet);','return ClientCommand::Release;')],'foreignJobRefused'),
  ('promote-unowned-frontend-packet', [('json_object_set_boolean_member(frame,"signaled",packet->signaled);','json_object_set_boolean_member(frame,"owned",TRUE);json_object_set_boolean_member(frame,"signaled",packet->signaled);')],'unownedPacketRefused')]:
  changed=out/name;shutil.copytree(out/'inputs',changed)
  header=changed/'native/retained_client_command.hpp';s=header.read_text()
  for old,new in edits:assert s.count(old)==1;s=s.replace(old,new)
  header.write_text(s)
  mutant_args=[*compileArgs];mutant_args[mutant_args.index('-o')+1]=str(changed/'checks');run(name+'-compile',mutant_args,cwd=changed)
  path=next(v for v in witnesses if witness in v);stdin,wanted=witnesses[path]
  actual=[json.loads(v) for v in run(name+'-replay',[str(changed/'checks')],stdin).splitlines()]
  assert actual!=wanted;mutants.append({'name':name,'witness':path,'differentObservableState':True})
 legacy_args=[*compileArgs];legacy_args[legacy_args.index('native/retained-client-command-replay.cpp')]='native/client-command-test.cpp';legacy_args[legacy_args.index('-o')+1]=str(out/'legacy')
 run('legacy-compile',legacy_args)
 legacy=json.loads(run('legacy-controls',[str(out/'legacy')]));assert legacy['passed'];report['unchangedLegacyDecoderControls']=legacy['checks']
 assert all(sha(root/rel)==value for rel,value in report['inputs'].items())
 report.update(passed=True,selectedNames=selected,namedScenarios=14,invariantSamples=100,coupledTraces=traces,statesCompared=sum(v['statesCompared'] for v in traces),unsafeMutantsDetected=4,mutants=mutants)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:700]}),flush=True);sys.exit(not report['passed'])
