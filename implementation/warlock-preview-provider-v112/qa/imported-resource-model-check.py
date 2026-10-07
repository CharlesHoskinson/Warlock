"""Couple Quint event traces to actual C/SCM_RIGHTS/GIO/Broker operations."""
import hashlib,json,pathlib,re,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];plugin=root.parent/'warlock-family-style-crop-capture-v19'
out=root/'qa'/('imported-resource-model-check-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tool='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
names=[str(p.relative_to(root)) for p in (root/'native').glob('*') if p.is_file()]+['spec/imported_resources.qnt','spec/imported_resources_tests.qnt',str(pathlib.Path(__file__).relative_to(root))]
report={'passed':False,'inputs':{rel:sha(root/rel) for rel in names},'pluginInputSHA256':sha(plugin/'native/capture-resources.hpp'),'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Explicit selected Quint scenarios and sampled event traces compared to actual controlled C factory/native tickets, authenticated synthetic Native socket/resource engine, original SCM_RIGHTS sealed capture descriptor, real ImportedClients/Broker mapping and GIO reader. Compare actual backend count files, FD closure, reader count, charge, retained proof/record and read/error outcomes after every event. Initial original capture/export release prefix held by actual acquisition; reconciliation dispatch is a control-history ghost, not a second policy authority. Fixture lock qualifies resource ownership under lock; original source-scope lock privacy is qualified separately. Original capture/counters/clock/deadline retained; native Core/window pixels/WebKit and full release remain open.'}
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
 shutil.copy2(plugin/'native/capture-resources.hpp',out/'inputs/native/capture-resources.hpp')
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']).stdout)
 args=['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/imported-resource-replay.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','-o',str(out/'checks'),*flags]
 run('compile',args)
 folder=out/'inputs/spec';selected=re.findall(r'run (\w+)\s*=',(folder/'imported_resources_tests.qnt').read_text());assert len(selected)==14
 run('typecheck',[tool,'typecheck','imported_resources_tests.qnt'],cwd=folder)
 run('selected',[tool,'test','imported_resources_tests.qnt','--main=imported_resources_tests','--backend=typescript','--match=^('+'|'.join(selected)+')$','--seed=1060031','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')],cwd=folder)
 assert len(list(out.glob('named-*.itf.json')))==14
 run('samples',[tool,'run','imported_resources.qnt','--main=imported_resources','--backend=typescript','--invariant=safety','--seed=1060032','--max-samples=200','--max-steps=40','--n-traces=8','--out-itf='+str(out/'sample-{seq}.itf.json')],cwd=folder)
 traces=[];witnesses={}
 for path in sorted(out.glob('*.itf.json')):
  states=[v['s'] for v in decode(json.loads(path.read_text()))['states']];wanted=[];count=0
  for state in states:
   if len(state['history'])==count:continue
   count=len(state['history']);wanted.append({k:v for k,v in state.items() if k!='history'})
  stdin='\n'.join(states[-1]['history'])+'\n'
  actual=[json.loads(v) for v in run('replay-'+path.stem,[str(out/'checks')],stdin).stdout.splitlines()]
  assert actual==wanted,(path.name,actual,wanted)
  traces.append({'trace':path.name,'statesCompared':len(actual),'normalOwnedExit':True});witnesses[path.name]=(stdin,wanted)
 mutants=[]
 for name,old,new,witness in [
  ('keep-reader-authorized-after-quarantine','if(quarantined)return {};',';','dispatchDeniesReadBeforePoll'),
  ('close-mapping-before-reader-drain','if(!broker.consumerComplete(entry,f.job))return false;','broker.consumerComplete(entry,f.job);','backendZeroKeepsReaderMapping')]:
  target=out/name;shutil.copytree(out/'inputs',target);p=target/'native/imported_clients.hpp';s=p.read_text();assert s.count(old)==1;p.write_text(s.replace(old,new))
  mutant=[*args];mutant[mutant.index('-o')+1]=str(target/'checks');run(name+'-compile',mutant,cwd=target)
  path=next(v for v in witnesses if witness in v);stdin,wanted=witnesses[path]
  result=run(name+'-replay',[str(target/'checks')],stdin,required=False)
  actual=[json.loads(v) for v in result.stdout.splitlines()];assert actual!=wanted,(name,result.stderr)
  mutants.append({'name':name,'compiled':True,'witness':path,'differentObservableState':True,'exitCode':result.returncode})
 assert all(sha(root/rel)==value for rel,value in report['inputs'].items()) and sha(plugin/'native/capture-resources.hpp')==report['pluginInputSHA256']
 report.update(passed=True,selectedNames=selected,namedScenarios=14,invariantSamples=200,coupledTraces=traces,statesCompared=sum(v['statesCompared'] for v in traces),unsafeCompiledVariantsDetected=2,mutants=mutants)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:1400]}),flush=True);sys.exit(not report['passed'])
