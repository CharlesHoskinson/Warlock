"""Selected local-feedback model coupled to optimized current Elm and real C outputs."""
import hashlib,json,os,pathlib,re,resource,shlex,shutil,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('feedback-check-'+str(time.time_ns()));OUT.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
TOOL=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint')
inputs={str(p.relative_to(ROOT)):sha(p) for folder in ['src','native','spec','qa'] for p in (ROOT/folder).glob('*') if p.is_file() and p.name!='current-build.json'}
report={'passed':False,'scope':scope,'inputs':inputs,'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'toolSHA256':sha(TOOL.resolve()),'projection':'Fixed native binding/incarnation/clock, current picker stamp and local feedback sequence/status/floor, known capturing/cancelling job and exact effect counts. Expiration is actual native feedback in C fixture, not a synthetic frontend clock. Model does not prove whole policy refinement, native capture, pixels, presentation or accessibility announcements.'}
def run(name,argv,input=None,cwd=None,env=None):
 p=subprocess.run(argv,cwd=cwd or OUT/'inputs',capture_output=True,text=True,timeout=180,input=input,env=env)
 (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'argv':argv,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr or p.stdout;return p.stdout
try:
 buildPath=next(ROOT.glob('qa/build-*/report.json'));build=json.loads(buildPath.read_text());assert build['passed']
 for name,value in build['inputs'].items():assert sha(ROOT/name)==value,name
 report['fullBuild']={'path':str(buildPath),'sha256':sha(buildPath)}
 for name in inputs:
  target=OUT/'inputs'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
 shutil.copy2(ROOT/'elm.json',OUT/'inputs/elm.json')
 from toolchain import verify,command
 pin=verify();shutil.copytree(ROOT/pin['elmHome'],OUT/'elm-home');env=dict(os.environ,ELM_HOME=str(OUT/'elm-home'))
 run('feedback-elm',command(['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/PreviewFeedbackReplay.elm','--optimize','--output='+str(OUT/'feedback-replay.js')]),env=env);verify();report['compiledElmSHA256']=sha(OUT/'feedback-replay.js')
 run('js-syntax',['node','--check','qa/feedback-replay.js'])
 controls=json.loads(run('guard-controls',['node','qa/feedback-replay.js',str(OUT/'feedback-replay.js'),'qa/native-source-fixture.json']));assert controls['passed'];report['guardControls']=controls
 flags=shlex.split(run('gio-flags',['pkg-config','--cflags','--libs','gio-unix-2.0','json-glib-1.0']));binary=OUT/'local-feedback-tests'
 run('c-compile',['g++','-std=c++20','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-Inative','native/local-feedback-test.cpp','native/imported-clients.cpp','native/preview-provider-bootstrap.cpp','native/preview_uri.cpp','-o',str(binary),*flags])
 native=json.loads(run('actual-c-elm',['node','qa/feedback-replay.js',str(OUT/'feedback-replay.js'),'qa/native-source-fixture.json','--native',str(binary)]));assert native['passed'];report['nativeFixtureControls']=native
 folder=OUT/'inputs/spec';names=re.findall(r'run (\w+)\s*=',(folder/'feedback_tests.qnt').read_text());assert len(names)==len(set(names))==9
 run('typecheck',[str(TOOL),'typecheck','feedback_tests.qnt'],cwd=folder)
 run('selected',[str(TOOL),'test','feedback_tests.qnt','--main=feedback_tests','--backend=typescript','--match=^('+'|'.join(names)+')$','--seed=720001','--max-samples=1','--out-itf='+str(OUT/'named-{test}-{seq}.itf.json')],cwd=folder)
 assert len(list(OUT.glob('named-*.itf.json')))==9
 run('samples',[str(TOOL),'run','feedback.qnt','--main=feedback','--backend=typescript','--invariant=safety','--seed=720002','--max-samples=100','--max-steps=32','--n-traces=12','--out-itf='+str(OUT/'sample-{seq}.itf.json')],cwd=folder)
 def decode(value):
  if isinstance(value,list):return [decode(v) for v in value]
  if isinstance(value,dict):
   if '#bigint' in value:return int(value['#bigint'])
   return {k:decode(v) for k,v in value.items()}
  return value
 traces=[]
 for path in sorted(OUT.glob('*.itf.json')):
  states=[row['s'] for row in decode(json.loads(path.read_text()))['states']];history=states[-1]['history']
  actual=json.loads(run('replay-'+path.stem,['node','qa/feedback-replay.js',str(OUT/'feedback-replay.js'),'qa/native-source-fixture.json','--replay'],input=json.dumps(history)))
  expected=[];count=0
  for state in states:
   if len(state['history'])==count:continue
   count=len(state['history']);expected.append({**state,'history':[]})
  assert actual==expected,(path.name,actual,expected)
  traces.append({'trace':path.name,'statesCompared':len(actual)})
 assert len(traces)==21
 report.update(selectedNames=names,namedScenarios=9,invariantSamples=100,coupledTraces=traces,statesCompared=sum(row['statesCompared'] for row in traces))
 assert all(sha(ROOT/name)==value for name,value in inputs.items()),'Source changed during feedback checks'
 report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}),flush=True);sys.exit(not report['passed'])
