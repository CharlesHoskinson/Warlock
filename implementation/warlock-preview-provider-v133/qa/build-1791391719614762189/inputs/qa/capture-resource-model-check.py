"""Compare Quint traces to actual plugin19 owned-map engine and GUI resource decoder."""
import hashlib,json,pathlib,re,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];plugin=root.parent/'warlock-family-style-crop-capture-v19'
out=root/'qa'/('capture-resource-model-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tool='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
names=[str(p.relative_to(root)) for p in (root/'native').glob('*') if p.is_file()]+['spec/capture_resources.qnt','spec/capture_resources_tests.qnt',str(pathlib.Path(__file__).relative_to(root))]
report={'passed':False,'inputs':{rel:sha(root/rel) for rel in names},'pluginInputSHA256':sha(plugin/'native/capture-resources.hpp'),'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Explicitly selected Quint scenarios and sampled traces compared to actual plugin19 resource engine/wire encoder on owned producer/export records with real sealed descriptors and actual GUI105 resource decoder/cursor. Original grant/capture intent derives from authenticated synthetic Native socket; metadata engine replay is in process. Does not qualify actual Core registry/window pixels, C controlled delivery (separate witnesses), captured FD import or WebKit/native release.'}
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
 shutil.copy2(plugin/'native/capture-resources.hpp',out/'inputs/native/capture-resources.hpp')
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']))
 args=['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/capture-resource-replay.cpp','-o',str(out/'checks'),*flags]
 run('compile',args)
 folder=out/'inputs/spec';selected=re.findall(r'run (\w+)\s*=',(folder/'capture_resources_tests.qnt').read_text());assert len(selected)==14
 run('typecheck',[tool,'typecheck','capture_resources_tests.qnt'],cwd=folder)
 run('selected',[tool,'test','capture_resources_tests.qnt','--main=capture_resources_tests','--backend=typescript','--match=^('+'|'.join(selected)+')$','--seed=1050031','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')],cwd=folder)
 assert len(list(out.glob('named-*.itf.json')))==14
 run('samples',[tool,'run','capture_resources.qnt','--main=capture_resources','--backend=typescript','--invariant=safety','--seed=1050032','--max-samples=200','--max-steps=40','--n-traces=8','--out-itf='+str(out/'sample-{seq}.itf.json')],cwd=folder)
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
 for name,header,old,new,witness in [
  ('retire-locked-native-producer','native/capture-resources.hpp','else if(locked)result.status=Status::PendingLock;','else if(locked && false)result.status=Status::PendingLock;','lockPreservesOriginalProducer'),
  ('retire-other-current-capture','native/capture-resources.hpp','if(probe.request==target.capture) {','if(probe.request) {','oldTargetCannotEraseOtherCapture'),
  ('publish-resource-cursor-before-status-validation','native/client_resources.hpp','const std::string_view status=Json::text(object,"status");','cursor={scope.binding,result.sequence,result.now};\n    const std::string_view status=Json::text(object,"status");','malformedReplyCannotAdvanceCursor')]:
  target=out/name;shutil.copytree(out/'inputs',target);p=target/header;s=p.read_text();assert s.count(old)==1;p.write_text(s.replace(old,new))
  mutant=[*args];mutant[mutant.index('-o')+1]=str(target/'checks');run(name+'-compile',mutant,cwd=target)
  path=next(v for v in witnesses if witness in v);stdin,wanted=witnesses[path]
  actual=[json.loads(v) for v in run(name+'-replay',[str(target/'checks')],stdin).splitlines()]
  assert actual!=wanted;mutants.append({'name':name,'compiled':True,'witness':path,'differentObservableState':True})
 assert all(sha(root/rel)==value for rel,value in report['inputs'].items())
 assert sha(plugin/'native/capture-resources.hpp')==report['pluginInputSHA256']
 report.update(passed=True,selectedNames=selected,namedScenarios=14,invariantSamples=200,coupledTraces=traces,statesCompared=sum(v['statesCompared'] for v in traces),unsafeMutantsDetected=3,mutants=mutants)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:900]}),flush=True);sys.exit(not report['passed'])
