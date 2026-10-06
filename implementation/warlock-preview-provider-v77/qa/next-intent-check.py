"""Explicitly selected successor model and actual C/socket/optimized Elm checks."""
import hashlib,json,pathlib,re,resource,shlex,shutil,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('next-intent-check-'+str(time.time_ns()));OUT.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
TOOL=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint')
inputs={str(p.relative_to(ROOT)):sha(p) for folder in ['native','spec','qa','src'] for p in (ROOT/folder).glob('*') if p.is_file() and p.name!='current-build.json'}
report={'passed':False,'scope':scope,'inputs':inputs,'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'toolSHA256':sha(TOOL.resolve()),'projection':'Actual bounded ImportedIntentLedger and demand/Broker ownership, fixed native identity and explicit expired/pending/successor stamps. Socket fixture tests actual C/bootstrap/receipt membership and optimized current Elm. No whole GUI refinement, compositor capture, hardware or assistive technology acceptance.'}
def run(name,argv,input=None,cwd=None):
 p=subprocess.run(argv,cwd=cwd or OUT/'inputs',capture_output=True,text=True,timeout=180,input=input)
 (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':argv,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr or p.stdout;return p.stdout
def decode(v):
 if isinstance(v,list):return [decode(x) for x in v]
 if isinstance(v,dict):return int(v['#bigint']) if '#bigint' in v else {k:decode(x) for k,x in v.items()}
 return v
try:
 buildPath=next(ROOT.glob('qa/build-*/report.json'));build=json.loads(buildPath.read_text());assert build['passed']
 for name,value in build['inputs'].items():assert sha(ROOT/name)==value,name
 report['fullBuild']={'path':str(buildPath),'sha256':sha(buildPath)}
 for name in inputs:
  target=OUT/'inputs'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
 binary=OUT/'checks';source=OUT/'inputs/qa/next-intent-checks.cpp'
 run('compile-model',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative',str(source),'-o',str(binary)])
 flags=shlex.split(run('gio-flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']));cbinary=OUT/'next-intent-tests'
 run('compile-c',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/next-intent-test.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','-o',str(cbinary),*flags])
 elm=buildPath.parent/'inputs/assets/feedback-replay.js';assert sha(elm)==build['artifacts']['assets/feedback-replay.js']
 coupled=json.loads(run('actual-c-elm',['node','qa/next-intent-wire.js',str(elm),str(cbinary)]));assert coupled['passed'];report['wireControls']=coupled
 folder=OUT/'inputs/spec';names=re.findall(r'run (\w+)\s*=',(folder/'next_intent_tests.qnt').read_text());assert len(names)==len(set(names))==10
 run('typecheck',[str(TOOL),'typecheck','next_intent_tests.qnt'],cwd=folder)
 run('selected',[str(TOOL),'test','next_intent_tests.qnt','--main=next_intent_tests','--backend=typescript','--match=^('+'|'.join(names)+')$','--seed=770001','--max-samples=1','--out-itf='+str(OUT/'named-{test}-{seq}.itf.json')],cwd=folder)
 assert len(list(OUT.glob('named-*.itf.json')))==10
 run('samples',[str(TOOL),'run','next_intent.qnt','--main=next_intent','--backend=typescript','--invariant=safety','--seed=770002','--max-samples=150','--max-steps=35','--n-traces=12','--out-itf='+str(OUT/'sample-{seq}.itf.json')],cwd=folder)
 traces=[]
 for path in sorted(OUT.glob('*.itf.json')):
  states=[row['s'] for row in decode(json.loads(path.read_text()))['states']];events=states[-1]['history'];wanted=[];count=0
  for state in states:
   if len(state['history'])==count:continue
   count=len(state['history']);wanted.append({k:v for k,v in state.items() if k!='history'})
  actual=[json.loads(line) for line in run('replay-'+path.stem,[str(binary)],input='\n'.join(events)+'\n').splitlines()]
  assert actual==wanted,(path.name,actual,wanted);traces.append({'trace':path.name,'statesCompared':len(actual)})
 assert len(traces)==22
 report.update(passed=True,selectedNames=names,namedScenarios=10,invariantSamples=150,coupledTraces=traces,statesCompared=sum(row['statesCompared'] for row in traces))
 assert all(sha(ROOT/name)==value for name,value in inputs.items()),'Source changed during checks'
except Exception as error:report['passed']=False;report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}),flush=True);sys.exit(not report['passed'])
