"""Explicit first-ticket output gate model coupled to original Native/C/JSC."""
import hashlib,json,pathlib,re,resource,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=pathlib.Path(__file__).resolve().parents[1];out=root/'qa'/('driver-output-refinement-'+str(time.time_ns()));out.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=root/'qa/policy-driver-output-gate-check-1791377264204546838';prior=json.loads((base/'report.json').read_text());assert prior['passed'];names=list(prior['inputs'])+['native/policy-driver-output-model-fixture.cpp','spec/driver_output_gate.qnt','spec/driver_output_gate_tests.qnt','qa/driver-output-model-trace.js','qa/driver-output-refinement.py']
report={'passed':False,'inputs':{n:sha(root/n) for n in names},'commands':[],'priorReport':{'path':str(base/'report.json'),'sha256':sha(base/'report.json')},'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Explicit first original ticket custody/notification/effect/data receipt/independent native confirmation model. A labeled stricter compiled reservation gate withholds capacity before effects; selected model states compare actual C recovery frontiers, actual capture count/charge/terminal status, original JSC known/demand and native refusal. Each trace drains original Native/Elm physical/journal/confirmation duties and closes normally. No actual output queue exhaustion, full lifecycle/resource/RSS model, real Core/window/renderer or release acceptance.'}
def run(name,args,cwd=None):
 p=subprocess.run(args,cwd=cwd or out/'inputs',capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':args,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr or p.stdout;return p.stdout
def decoded(v):
 if isinstance(v,list):return [decoded(x) for x in v]
 if isinstance(v,dict):return int(v['#bigint']) if '#bigint' in v else {k:decoded(x) for k,x in v.items()}
 return v
try:
 for rel,value in prior['inputs'].items():assert sha(root/rel)==value,rel
 for rel,value in prior['artifacts'].items():assert sha(base/rel)==value,rel
 for rel in names:
  p=out/'inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/rel,p)
 shutil.copy2(base/'inputs/native/capture-resources.hpp',out/'inputs/native/capture-resources.hpp')
 tool='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint';folder=out/'inputs/spec';selected=re.findall(r'run (\w+)\s*=',(folder/'driver_output_gate_tests.qnt').read_text());assert len(selected)==8
 run('typecheck',[tool,'typecheck','driver_output_gate_tests.qnt'],folder)
 run('selected',[tool,'test','driver_output_gate_tests.qnt','--main=driver_output_gate_tests','--backend=typescript','--match=^('+'|'.join(selected)+')$','--seed=1210001','--max-samples=1','--out-itf='+str(out/'named-{test}-{seq}.itf.json')],folder);traces=sorted(out.glob('named-*.itf.json'));assert len(traces)==8
 run('samples',[tool,'run','driver_output_gate.qnt','--main=driver_output_gate','--backend=typescript','--invariant=safety','--seed=1210002','--max-samples=200','--max-steps=32','--out-itf='+str(out/'samples.itf.json')],folder)
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0','javascriptcoregtk-4.1']));binary=out/'driver'
 run('compile-model-fixture',['g++','-std=c++20','-O1','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/policy-driver-output-model-fixture.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','native/elm-preview-policy.cpp','-o',str(binary),*flags])
 run('controller-syntax',['node','--check','qa/driver-output-model-trace.js']);report['coupledTraces']=[]
 for index,path in enumerate(traces):
  data=decoded(json.loads(path.read_text()));states=[r['s'] for r in data['states']];scenario=out/('scenario-'+str(index));scenario.mkdir();trace=scenario/'model-states.json';trace.write_text(json.dumps(states,indent=2)+'\n')
  evidence=json.loads(run('native-trace-'+str(index),['node',str(out/'inputs/qa/driver-output-model-trace.js'),str(binary),str(base/'policy.js'),str(out/'inputs/assets/native-preview-control-outbox.js'),str(trace)],scenario));assert evidence['passed'] and evidence['normalOwnedExit'] and evidence['normalOwnedPeerExit'] and evidence['nativeGrantResets']==0
  report['coupledTraces'].append({'name':path.name,'states':len(states),'evidence':evidence})
 report['namedScenarios']=len(selected);report['invariantSamples']=200;report['observableStatesCompared']=sum(r['evidence']['observations'] for r in report['coupledTraces']);assert all(sha(root/n)==v for n,v in report['inputs'].items());report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':str(report.get('error',''))[:2200]}),flush=True);sys.exit(not report['passed'])
